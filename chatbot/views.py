from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import ChatConversation, ChatMessage
from agents.orchestrator import AgentOrchestrator

@login_required
def chatbot_view(request):
    """View to display the interactive AI Career Chatbot interface and handle user prompts."""
    # Retrieve active conversation or create new
    conversation = ChatConversation.objects.filter(user=request.user).order_by('-created_at').first()
    if not conversation:
        conversation = ChatConversation.objects.create(user=request.user, title="Career Advisory Session")

    if request.method == 'POST':
        user_message_text = request.POST.get('message', '').strip()
        if user_message_text:
            # 1. Save User Message
            ChatMessage.objects.create(
                conversation=conversation,
                sender='user',
                message=user_message_text,
                agent_type='Orchestrator'
            )

            # 2. Process via Agent Orchestrator
            orchestrator = AgentOrchestrator()
            ai_response_text, agent_name = orchestrator.route_and_process(request.user, user_message_text)

            # 3. Save AI Message
            ai_msg = ChatMessage.objects.create(
                conversation=conversation,
                sender='ai',
                message=ai_response_text,
                agent_type=agent_name
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'user_message': user_message_text,
                    'ai_response': ai_response_text,
                    'agent_type': agent_name,
                    'timestamp': ai_msg.timestamp.strftime('%H:%M')
                })

            return redirect('chatbot')

    chat_messages = conversation.messages.all()

    context = {
        'conversation': conversation,
        'chat_messages': chat_messages,
    }
    return render(request, 'chatbot/chat.html', context)

@login_required
def clear_chat_view(request):
    """Starts a new chat session."""
    ChatConversation.objects.create(user=request.user, title="New Career Advisory Session")
    messages.success(request, "New chat conversation started!")
    return redirect('chatbot')
