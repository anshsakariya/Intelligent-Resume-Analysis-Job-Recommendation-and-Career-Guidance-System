from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Roadmap, RoadmapTask
from agents.planner_agent import PlannerAgent
from skills.models import UserSkill

@login_required
def roadmap_view(request):
    """View to render personalized learning roadmap, skill gap overview, and task checklist."""
    agent = PlannerAgent()
    gap_info = agent.identify_skill_gap(request.user)

    active_roadmap = Roadmap.objects.filter(user=request.user).order_by('-created_at').first()

    if request.method == 'POST' and 'regenerate' in request.POST:
        hours = int(request.POST.get('hours_per_day', 2))
        days = int(request.POST.get('days_per_week', 5))
        active_roadmap = agent.generate_roadmap(request.user, hours_per_day=hours, days_per_week=days)
        messages.success(request, f"New personalized career roadmap generated for {request.user.profile.target_role}!")
        return redirect('roadmap')

    if not active_roadmap:
        active_roadmap = agent.generate_roadmap(request.user)

    tasks = active_roadmap.tasks.all()
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()
    progress_pct = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Group tasks by phase
    phases = {}
    for task in tasks:
        phases.setdefault(task.phase_name, []).append(task)

    context = {
        'roadmap': active_roadmap,
        'phases': phases,
        'progress_pct': progress_pct,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'existing_skills': gap_info['existing_skills'],
        'missing_skills': gap_info['missing_skills'],
    }
    return render(request, 'roadmap/index.html', context)

@login_required
def toggle_task_status_view(request, task_id):
    """POST view to update a roadmap task status (Completed / In Progress / Pending)."""
    task = get_object_or_404(RoadmapTask, pk=task_id, roadmap__user=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status', 'Completed')
        task.status = new_status
        if new_status == 'Completed':
            task.completed_at = timezone.now()
        else:
            task.completed_at = None
        task.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Recalculate progress
            roadmap = task.roadmap
            total = roadmap.tasks.count()
            completed = roadmap.tasks.filter(status='Completed').count()
            pct = int((completed / total) * 100) if total > 0 else 0
            return JsonResponse({'status': 'success', 'progress_pct': pct, 'task_status': task.status})

        messages.success(request, f"Task '{task.title}' updated to {task.status}.")

    return redirect('roadmap')
