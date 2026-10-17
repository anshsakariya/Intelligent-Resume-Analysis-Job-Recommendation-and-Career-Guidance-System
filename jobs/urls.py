from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list_view, name='job_recommendations'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('<int:job_id>/apply/', views.job_apply_view, name='job_apply'),
]

