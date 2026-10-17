from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import UserRegistrationForm, UserUpdateForm, UserProfileForm
from .models import Profile

def home_view(request):
    """Landing Page View."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register_view(request):
    """User Registration View."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! Please log in below.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors highlighted below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """User Login View."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
@require_POST
def logout_view(request):
    """User Logout View."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def profile_view(request):
    """User Profile Editing View."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=profile)

    latest_resume = None
    latest_analysis = None
    try:
        from resumes.models import Resume
        latest_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        if latest_resume and hasattr(latest_resume, 'analysis'):
            latest_analysis = latest_resume.analysis
    except Exception:
        pass

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'latest_resume': latest_resume,
        'latest_analysis': latest_analysis,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def dashboard_view(request):
    """Main Analytics & Dashboard Overview View."""
    user = request.user
    profile = getattr(user, 'profile', None)

    # Safely retrieve user data across apps (will connect to models as they are created)
    latest_resume = None
    latest_analysis = None
    existing_skills = []
    missing_skills = []
    recommended_jobs = []
    active_roadmap = None
    roadmap_tasks = []
    roadmap_progress = 0
    recent_chats = []

    # Get Resume & Analysis
    from resumes.models import Resume
    latest_resume = Resume.objects.filter(user=user).order_by('-uploaded_at').first()
    if latest_resume:
        latest_analysis = getattr(latest_resume, 'analysis', None)
        if latest_analysis is None:
            from agents.resume_agent import ResumeAgent
            latest_analysis = ResumeAgent().analyze_resume(latest_resume)

    # Only show skill progress once a resume has been analyzed.
    if latest_analysis:
        from agents.planner_agent import PlannerAgent
        skill_gap = PlannerAgent().identify_skill_gap(user)
        existing_skills = skill_gap['existing_skills']
        missing_skills = skill_gap['missing_skills']

    # Get Job Recommendations (distinct jobs only)
    try:
        from recommendations.models import JobRecommendation
        all_recs = JobRecommendation.objects.filter(user=user).select_related('job').order_by('-match_score')
        seen_dash = set()
        for r in all_recs:
            key = (r.job.title.lower().strip(), r.job.company.lower().strip())
            if key not in seen_dash:
                seen_dash.add(key)
                recommended_jobs.append(r)
                if len(recommended_jobs) >= 4:
                    break
    except Exception:
        pass

    # Get Roadmap & Progress
    try:
        from roadmap.models import Roadmap, RoadmapTask
        active_roadmap = Roadmap.objects.filter(user=user).prefetch_related('tasks').order_by('-created_at').first()
        if active_roadmap:
            roadmap_tasks = list(active_roadmap.tasks.all())
            total_tasks = len(roadmap_tasks)
            completed_tasks = sum(1 for t in roadmap_tasks if t.status == 'Completed')
            roadmap_progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    except Exception:
        pass

    # Get Chat History
    try:
        from chatbot.models import ChatConversation
        recent_chats = ChatConversation.objects.filter(user=user).order_by('-created_at')[:5]
    except Exception:
        pass

    context = {
        'profile': profile,
        'latest_resume': latest_resume,
        'latest_analysis': latest_analysis,
        'existing_skills': existing_skills,
        'missing_skills': missing_skills,
        'recommended_jobs': recommended_jobs,
        'active_roadmap': active_roadmap,
        'roadmap_tasks': roadmap_tasks,
        'roadmap_progress': roadmap_progress,
        'recent_chats': recent_chats,
    }
    return render(request, 'dashboard.html', context)
