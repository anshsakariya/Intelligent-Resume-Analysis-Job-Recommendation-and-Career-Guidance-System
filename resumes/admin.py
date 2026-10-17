from django.contrib import admin
from .models import Resume, ResumeAnalysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'ats_score', 'uploaded_at')
    search_fields = ('user__username', 'extracted_text')
    list_filter = ('uploaded_at',)

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'ats_score', 'skills_score', 'keyword_score', 'analyzed_at')
    search_fields = ('resume__user__username',)
