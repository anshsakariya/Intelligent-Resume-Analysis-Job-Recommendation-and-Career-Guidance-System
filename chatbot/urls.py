from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('new/', views.clear_chat_view, name='new_chat'),
]
