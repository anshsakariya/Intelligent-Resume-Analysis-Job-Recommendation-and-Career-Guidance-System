from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'experience_level', 'location', 'employment_type', 'posted_date')
    search_fields = ('title', 'company', 'description', 'location')
    list_filter = ('experience_level', 'employment_type', 'posted_date')
    filter_horizontal = ('required_skills', 'preferred_skills')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'job', 'status', 'applied_at')
    search_fields = ('full_name', 'email', 'job__title', 'job__company', 'phone')
    list_filter = ('status', 'applied_at', 'experience_years')
    list_editable = ('status',)

