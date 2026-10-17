from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'target_role', 'experience_level', 'education', 'created_at')
    search_fields = ('user__username', 'full_name', 'target_role', 'education', 'university')
    list_filter = ('target_role', 'experience_level', 'created_at')
