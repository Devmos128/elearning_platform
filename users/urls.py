from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Core
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('post-status/', views.post_status_update, name='post_status_update'),
    path('search-users/', views.search_users, name='search_users'),
    
    # Student Management
    path('manage-students/', views.manage_students, name='manage_students'),
    path('block-student/<int:student_id>/', views.block_student, name='block_student'),
    path('unblock-student/<int:student_id>/', views.unblock_student, name='unblock_student'),
    path('remove-student/<int:course_id>/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
