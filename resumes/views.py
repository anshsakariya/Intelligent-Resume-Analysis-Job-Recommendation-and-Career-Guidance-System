from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Resume, ResumeAnalysis
from .forms import ResumeUploadForm
from .services import extract_resume_text
from agents.resume_agent import ResumeAgent
from skills.models import UserSkill

@login_required
def upload_resume_view(request):
    """View to handle PDF Resume Upload and automatic trigger of text extraction & ResumeAgent."""
    latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.original_name = request.FILES['file'].name  # Save original filename
            resume.save()

            # 1. Extract PDF text with multi-source fallback
            file_obj = request.FILES.get('file')
            extracted_text = ""
            if file_obj:
                try:
                    file_obj.seek(0)
                    extracted_text = extract_resume_text(file_obj)
                except Exception as e:
                    print(f"Extract from uploaded file error: {e}")

            if not extracted_text:
                try:
                    with resume.file.open('rb') as uploaded_file:
                        extracted_text = extract_resume_text(uploaded_file)
                except Exception as e:
                    print(f"Extract from resume.file error: {e}")

            if not extracted_text:
                messages.warning(request, "Uploaded PDF file was empty or text could not be read cleanly. We performed basic analysis.")

            resume.extracted_text = extracted_text
            resume.save()

            # 2. Trigger ResumeAgent analysis
            agent = ResumeAgent()
            agent.analyze_resume(resume)

            # 3. Immediately trigger fresh AI job recommendations
            try:
                from jobs.services import recommend_jobs_for_user
                recommend_jobs_for_user(request.user, force_refresh=True)
            except Exception as e:
                print(f"Auto-refresh recommendations error: {e}")

            messages.success(request, f"Resume uploaded and analyzed successfully! ATS Score: {resume.ats_score}/100")
            return redirect('resume_analysis')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ResumeUploadForm()

    context = {
        'form': form,
        'latest_resume': latest_resume
    }
    return render(request, 'resumes/upload.html', context)

@login_required
def resume_analysis_view(request):
    """View displaying detailed ATS score breakdown, strengths, weaknesses, and suggestions."""
    latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    
    if not latest_resume:
        messages.info(request, "Please upload your resume to see your ATS score and career suggestions.")
        return redirect('upload_resume')

    analysis = getattr(latest_resume, 'analysis', None)
    if not analysis or request.GET.get('reanalyze') == '1':
        # Trigger or refresh analysis
        agent = ResumeAgent()
        analysis = agent.analyze_resume(latest_resume)
        if request.GET.get('reanalyze') == '1':
            messages.success(request, f"Resume re-analyzed! Updated ATS Score: {analysis.ats_score}/100")

    extracted_skills = UserSkill.objects.filter(user=request.user, is_extracted=True).select_related('skill')

    context = {
        'resume': latest_resume,
        'analysis': analysis,
        'extracted_skills': extracted_skills,
    }
    return render(request, 'resumes/analysis.html', context)

from django.http import FileResponse, Http404

@login_required
def resume_download_view(request, resume_id):
    """
    Directly downloads the generated PDF file.
    """
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if not resume.file:
        raise Http404("Resume file not found.")
    
    response = FileResponse(resume.file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.original_name or "Resume.pdf"}"'
    return response
