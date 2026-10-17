from django.urls import path
from . import views

urlpatterns = [
    path('', views.roadmap_view, name='roadmap'),
    path('task/<int:task_id>/toggle/', views.toggle_task_status_view, name='toggle_task_status'),
]
