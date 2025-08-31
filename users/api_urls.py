from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list_api, name='user_list_api'),
    path('users/<int:user_id>/', views.user_detail_api, name='user_detail_api'),
]
