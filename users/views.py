from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .forms import CustomUserCreationForm, StatusUpdateForm, UserSearchForm
from .models import User, StatusUpdate, UserProfile, Notification
from courses.models import Course


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def home(request):
    user = request.user
    status_updates = StatusUpdate.objects.filter(user=user).order_by('-created_at')[:5]
    
    if user.is_student():
        enrolled_courses = user.profile.courses_enrolled.all()
        upcoming_deadlines = user.profile.upcoming_deadlines.all()
    else:
        enrolled_courses = Course.objects.filter(teacher=user)
        upcoming_deadlines = []
    
    context = {
        'user': user,
        'status_updates': status_updates,
        'enrolled_courses': enrolled_courses,
        'upcoming_deadlines': upcoming_deadlines,
    }
    return render(request, 'users/home.html', context)


@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    status_updates = StatusUpdate.objects.filter(user=user).order_by('-created_at')
    
    if request.user.is_student():
        enrolled_courses = user.profile.courses_enrolled.all()
    else:
        enrolled_courses = Course.objects.filter(teacher=user)
    
    context = {
        'profile_user': user,
        'status_updates': status_updates,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'users/profile.html', context)


@login_required
def post_status_update(request):
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status_update = form.save(commit=False)
            status_update.user = request.user
            status_update.save()
            messages.success(request, 'Status update posted!')
        else:
            messages.error(request, 'Error posting status update.')
    
    return redirect('home')


@login_required
def search_users(request):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can search for users.')
        return redirect('home')
    
    form = UserSearchForm(request.GET)
    users = []
    
    if form.is_valid() and form.cleaned_data.get('search_query'):
        query = form.cleaned_data['search_query']
        user_type = form.cleaned_data.get('user_type')
        
        q_objects = Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        
        if user_type:
            q_objects &= Q(user_type=user_type)
        
        users = User.objects.filter(q_objects).exclude(id=request.user.id)
    
    context = {
        'form': form,
        'users': users,
    }
    return render(request, 'users/search_users.html', context)



@login_required
def manage_students(request):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can access student management.')
        return redirect('home')
    
    teacher_courses = Course.objects.filter(teacher=request.user)
    enrolled_students = User.objects.filter(
        enrolled_courses__in=teacher_courses
    ).distinct().order_by('username')
    
    context = {
        'enrolled_students': enrolled_students,
        'teacher_courses': teacher_courses,
    }
    return render(request, 'users/manage_students.html', context)


@login_required
def block_student(request, student_id):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can block students.')
        return redirect('home')
    
    try:
        student = User.objects.get(id=student_id, user_type='student')
        
        teacher_courses = Course.objects.filter(teacher=request.user)
        if not student.enrolled_courses.filter(id__in=teacher_courses.values_list('id', flat=True)).exists():
            messages.error(request, 'You can only block students enrolled in your courses.')
            return redirect('manage_students')
        
        student.block_user(request.user)
        messages.success(request, f'{student.get_full_name() or student.username} has been blocked.')
        
    except User.DoesNotExist:
        messages.error(request, 'Student not found.')
    
    return redirect('manage_students')


@login_required
def unblock_student(request, student_id):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can unblock students.')
        return redirect('home')
    
    try:
        student = User.objects.get(id=student_id, user_type='student')
        
        if student.blocked_by != request.user:
            messages.error(request, 'You can only unblock students that you blocked.')
            return redirect('manage_students')
        
        student.unblock_user(request.user)
        messages.success(request, f'{student.get_full_name() or student.username} has been unblocked.')
        
    except User.DoesNotExist:
        messages.error(request, 'Student not found.')
    
    return redirect('manage_students')


@login_required
def remove_student_from_course(request, course_id, student_id):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can remove students from courses.')
        return redirect('home')
    
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
        student = User.objects.get(id=student_id, user_type='student')
        
        if not course.students.filter(id=student.id).exists():
            messages.error(request, 'Student is not enrolled in this course.')
            return redirect('course_students', course_id=course_id)
        
        course.students.remove(student)
        
        from users.models import Notification
        Notification.create_removal_notification(student, course, request.user)
        
        messages.success(request, f'{student.get_full_name() or student.username} has been removed from {course.title}.')
        
    except (Course.DoesNotExist, User.DoesNotExist):
        messages.error(request, 'Course or student not found.')
    
    return redirect('course_students', course_id=course_id)


@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'users/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.mark_as_read()
        messages.success(request, 'Notification marked as read.')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found.')
    
    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_api(request):
    users = User.objects.all()
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'email': user.email,
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_api(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_type': user.user_type,
        'email': user.email,
        'bio': user.bio,
        'date_joined': user.date_joined,
    }
    return Response(data)
