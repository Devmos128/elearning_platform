from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Course, CourseMaterial, Assignment, Feedback, Enrollment
from .forms import CourseForm, CourseMaterialForm, AssignmentForm, FeedbackForm

User = get_user_model()


@login_required
def course_list(request):
    if request.user.is_teacher():
        courses = Course.objects.filter(teacher=request.user)
    else:
        courses = Course.objects.filter(is_active=True)
    
    context = {
        'courses': courses,
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    materials = course.materials.all()
    assignments = course.assignments.all()
    feedback = course.feedback.all()
    
    # Check if student is enrolled
    is_enrolled = False
    if request.user.is_student():
        is_enrolled = course.students.filter(id=request.user.id).exists()
    
    context = {
        'course': course,
        'materials': materials,
        'assignments': assignments,
        'feedback': feedback,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def create_course(request):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can create courses.')
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    context = {
        'form': form,
    }
    return render(request, 'courses/create_course.html', context)


@login_required
def upload_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if not request.user.is_teacher() or course.teacher != request.user:
        messages.error(request, 'You do not have permission to upload materials for this course.')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material uploaded successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseMaterialForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/upload_material.html', context)


@login_required
def enroll_course(request, course_id):
    if not request.user.is_student():
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    if course.students.filter(id=request.user.id).exists():
        messages.warning(request, 'You are already enrolled in this course.')
    else:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('course_detail', course_id=course.id)


@login_required
def leave_course(request, course_id):
    if not request.user.is_student():
        messages.error(request, 'Only students can leave courses.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if enrollment:
        enrollment.delete()
        messages.success(request, f'Successfully left {course.title}.')
    else:
        messages.warning(request, 'You are not enrolled in this course.')
    
    return redirect('course_list')


@login_required
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if not request.user.is_teacher() or course.teacher != request.user:
        messages.error(request, 'You do not have permission to view this course\'s students.')
        return redirect('course_list')
    
    students = course.students.all()
    
    context = {
        'course': course,
        'students': students,
    }
    return render(request, 'courses/course_students.html', context)


def remove_student_from_course(request, course_id, student_id):
    """Remove a student from a specific course"""
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can remove students from courses.')
        return redirect('course_list')
    
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
        student = User.objects.get(id=student_id, user_type='student')
        
        # Check if student is enrolled in this course
        if not course.students.filter(id=student.id).exists():
            messages.error(request, 'Student is not enrolled in this course.')
            return redirect('course_students', course_id=course_id)
        
        # Remove student from course
        course.students.remove(student)
        
        # Create notification for the removed student
        from users.models import Notification
        Notification.create_removal_notification(student, course, request.user)
        
        messages.success(request, f'{student.get_full_name() or student.username} has been removed from {course.title}.')
        
    except (Course.DoesNotExist, User.DoesNotExist):
        messages.error(request, 'Course or student not found.')
    
    return redirect('course_students', course_id=course_id)


@login_required
def delete_course(request, course_id):
    """Delete a course (only by the creator)"""
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can delete courses.')
        return redirect('course_list')
    
    try:
        course = Course.objects.get(id=course_id, teacher=request.user)
        course_title = course.title
        
        # Get all enrolled students for notifications
        enrolled_students = course.students.all()
        
        # Create notifications for all enrolled students
        from users.models import Notification
        for student in enrolled_students:
            Notification.objects.create(
                user=student,
                notification_type='removed',
                title='Course Deleted',
                message=f'The course "{course_title}" has been deleted by {request.user.get_full_name() or request.user.username}. You are no longer enrolled in this course.',
                related_user=request.user,
                related_course=course
            )
        
        # Delete the course
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted successfully.')
        
    except Course.DoesNotExist:
        messages.error(request, 'Course not found or you do not have permission to delete it.')
    
    return redirect('course_list')


@login_required
def leave_feedback(request, course_id):
    if not request.user.is_student():
        messages.error(request, 'Only students can leave feedback.')
        return redirect('course_list')
    
    course = get_object_or_404(Course, id=course_id)
    
    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, 'You must be enrolled in the course to leave feedback.')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback, created = Feedback.objects.get_or_create(
                student=request.user,
                course=course,
                defaults=form.cleaned_data
            )
            if not created:
                feedback.rating = form.cleaned_data['rating']
                feedback.comment = form.cleaned_data['comment']
                feedback.save()
            
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = FeedbackForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/leave_feedback.html', context)
