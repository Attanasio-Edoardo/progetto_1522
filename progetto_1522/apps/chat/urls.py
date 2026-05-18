"""apps/chat/urls.py"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:ticket_id>/', views.chat_room, name='room'),
]
