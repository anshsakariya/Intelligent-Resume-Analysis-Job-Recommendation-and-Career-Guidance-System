from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Job, JobApplication
from .forms import JobApplicationForm
from recommendations.models import JobRecommendation
from resumes.models import Resume
from agents.job_agent import JobAgent

@login_required
def job_list_view(request):
    """View to display personalized job recommendations using JobAgent & ML engine."""
    force_refresh = request.GET.get('refresh') == '1'
    agent = JobAgent()
    recommendations = agent.recommend_jobs(request.user, force_refresh=force_refresh)

    # Filtering options
    exp_filter = request.GET.get('experience', '')
    if exp_filter:
        recommendations = [r for r in recommendations if r.job.experience_level == exp_filter]

    # Ensure distinct jobs only (no duplicate cards)
    seen_jobs = set()
    unique_recs = []
    for r in recommendations:
        key = (r.job.title.lower().strip(), r.job.company.lower().strip())
        if key not in seen_jobs:
            seen_jobs.add(key)
            unique_recs.append(r)
    recommendations = unique_recs

    # Applied job IDs for current user
    applied_job_ids = set(JobApplication.objects.filter(user=request.user).values_list('job_id', flat=True))

    context = {
        'recommendations': recommendations,
        'selected_exp': exp_filter,
        'applied_job_ids': applied_job_ids,
    }
    return render(request, 'jobs/list.html', context)

@login_required
def job_detail_view(request, job_id):
    """View displaying detailed job information, AI match breakdown, and application status."""
    job = get_object_or_404(Job.objects.prefetch_related('required_skills', 'preferred_skills'), pk=job_id)
    recommendation = JobRecommendation.objects.filter(user=request.user, job=job).first()

    if not recommendation:
        agent = JobAgent()
        agent.recommend_jobs(request.user)
        recommendation = JobRecommendation.objects.filter(user=request.user, job=job).first()

    user_application = JobApplication.objects.filter(user=request.user, job=job).first()

    context = {
        'job': job,
        'recommendation': recommendation,
        'user_application': user_application,
    }
    return render(request, 'jobs/detail.html', context)

@login_required
def job_apply_view(request, job_id):
    """View to handle submitting job application form."""
    job = get_object_or_404(Job, pk=job_id)
    
    # Check if already applied
    existing_application = JobApplication.objects.filter(user=request.user, job=job).first()
    if existing_application:
        messages.info(request, f"You have already applied for '{job.title}' at {job.company}.")
        return redirect('job_detail', job_id=job.id)

    profile = getattr(request.user, 'profile', None)
    initial_data = {
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'email': request.user.email,
        'phone': profile.phone if profile else '',
        'experience_years': profile.experience_level if profile else '0-2 years',
    }

    latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    if latest_resume:
        initial_data['resume'] = latest_resume.id

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            
            # If no specific resume selected or uploaded, auto-link latest resume
            if not application.resume and not application.custom_resume_file and latest_resume:
                application.resume = latest_resume

            application.save()
            messages.success(request, f"Application for '{job.title}' at {job.company} submitted successfully!")
            return redirect('job_detail', job_id=job.id)
        else:
            messages.error(request, "Please correct the errors in the application form.")
    else:
        form = JobApplicationForm(initial=initial_data, user=request.user)

    context = {
        'job': job,
        'form': form,
        'latest_resume': latest_resume,
    }
    return render(request, 'jobs/apply.html', context)

@login_required
def my_applications_view(request):
    """View to list all job applications submitted by the current user."""
    applications = JobApplication.objects.filter(user=request.user).select_related('job').order_by('-applied_at')
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)

