from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('create/', views.create_chat_room, name='create_chat_room'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('<str:room_name>/delete/', views.delete_chat_room, name='delete_chat_room'),
]
