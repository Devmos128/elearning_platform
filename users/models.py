from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(null=True, blank=True)
    blocked_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_users')
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_teacher(self):
        return self.user_type == 'teacher'
    
    def is_student(self):
        return self.user_type == 'student'
    
    def block_user(self, blocked_by):
        """Block a user from accessing the system"""
        self.is_blocked = True
        self.blocked_at = timezone.now()
        self.blocked_by = blocked_by
        self.save()
        

        Notification.objects.create(
            user=self,
            notification_type='blocked',
            title='Account Blocked',
            message=f'Your account has been blocked by {blocked_by.get_full_name() or blocked_by.username}. Please contact support for assistance.',
            related_user=blocked_by
        )
    
    def unblock_user(self, unblocked_by):
        """Unblock a user"""
        self.is_blocked = False
        self.blocked_at = None
        self.blocked_by = None
        self.save()
        

        Notification.objects.create(
            user=self,
            notification_type='unblocked',
            title='Account Unblocked',
            message=f'Your account has been unblocked by {unblocked_by.get_full_name() or unblocked_by.username}. You can now access the system.',
            related_user=unblocked_by
        )


class StatusUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_updates')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}..."


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    courses_enrolled = models.ManyToManyField('courses.Course', blank=True, related_name='enrolled_students')
    upcoming_deadlines = models.ManyToManyField('courses.Assignment', blank=True, related_name='assigned_students')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('enrollment', 'Course Enrollment'),
        ('material', 'New Course Material'),
        ('blocked', 'Account Blocked'),
        ('unblocked', 'Account Unblocked'),
        ('removed', 'Removed from Course'),
        ('assignment', 'New Assignment'),
        ('feedback', 'Course Feedback'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    related_course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    related_material = models.ForeignKey('courses.CourseMaterial', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):

        self.is_read = True
        self.save()
    
    @classmethod
    def create_enrollment_notification(cls, student, course, teacher):
        cls.objects.create(
            user=teacher,
            notification_type='enrollment',
            title='New Student Enrollment',
            message=f'{student.get_full_name() or student.username} has enrolled in your course "{course.title}".',
            related_user=student,
            related_course=course
        )
    
    @classmethod
    def create_material_notification(cls, course, material, teacher):

        enrolled_students = course.students.all()
        for student in enrolled_students:
            cls.objects.create(
                user=student,
                notification_type='material',
                title='New Course Material',
                message=f'New material "{material.title}" has been added to course "{course.title}" by {teacher.get_full_name() or teacher.username}.',
                related_user=teacher,
                related_course=course,
                related_material=material
            )
    
    @classmethod
    def create_removal_notification(cls, student, course, teacher):
        cls.objects.create(
            user=student,
            notification_type='removed',
            title='Removed from Course',
            message=f'You have been removed from the course "{course.title}" by {teacher.get_full_name() or teacher.username}.',
            related_user=teacher,
            related_course=course
        )
