from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume_view, name='upload_resume'),
    path('analysis/', views.resume_analysis_view, name='resume_analysis'),
    path('download/<int:resume_id>/', views.resume_download_view, name='resume_download'),
]
