from django.contrib import admin
from .models import Roadmap, RoadmapTask

class RoadmapTaskInline(admin.TabularInline):
    model = RoadmapTask
    extra = 1

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_role', 'hours_per_day', 'days_per_week', 'created_at')
    search_fields = ('user__username', 'target_role')
    inlines = [RoadmapTaskInline]

@admin.register(RoadmapTask)
class RoadmapTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'phase_name', 'priority', 'status', 'order')
    search_fields = ('title', 'roadmap__user__username', 'phase_name')
    list_filter = ('status', 'priority', 'phase_name')
