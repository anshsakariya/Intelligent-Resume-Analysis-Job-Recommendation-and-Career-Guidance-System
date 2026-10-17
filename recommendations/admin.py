from django.contrib import admin
from .models import JobRecommendation

@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'match_score', 'created_at')
    search_fields = ('user__username', 'job__title', 'job__company')
    list_filter = ('match_score', 'created_at')
