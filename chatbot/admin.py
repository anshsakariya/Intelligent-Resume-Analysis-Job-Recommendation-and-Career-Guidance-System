from django.contrib import admin
from .models import ChatConversation, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 1

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    search_fields = ('user__username', 'title')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'agent_type', 'timestamp')
    search_fields = ('conversation__user__username', 'message')
    list_filter = ('sender', 'agent_type', 'timestamp')
