from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/upload-material/', views.upload_material, name='upload_material'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/leave/', views.leave_course, name='leave_course'),
    path('<int:course_id>/students/', views.course_students, name='course_students'),
    path('<int:course_id>/feedback/', views.leave_feedback, name='leave_feedback'),
    path('<int:course_id>/remove-student/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
    path('<int:course_id>/delete/', views.delete_course, name='delete_course'),
]
