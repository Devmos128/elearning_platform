from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile, StatusUpdate
from courses.models import Course, CourseMaterial, Assignment, Feedback, Enrollment
from chat.models import ChatRoom, Message
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up demo data for the eLearning platform'

    def handle(self, *args, **options):
        self.stdout.write('Setting up demo data...')

        # Create demo users
        self.create_demo_users()
        
        # Create demo courses
        self.create_demo_courses()
        
        # Create demo chat rooms
        self.create_demo_chat_rooms()
        
        # Create demo status updates
        self.create_demo_status_updates()
        
        # Create demo feedback
        self.create_demo_feedback()

        self.stdout.write(
            self.style.SUCCESS('Successfully set up demo data!')
        )

    def create_demo_users(self):
        # Create teacher
        teacher, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'user_type': 'teacher',
                'bio': 'Experienced computer science instructor with 10+ years of teaching experience.',
                'is_staff': True,
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            UserProfile.objects.create(user=teacher)
            self.stdout.write(f'Created teacher: {teacher.username}')

        # Create students
        students_data = [
            {
                'username': 'student1',
                'email': 'student1@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'bio': 'Computer science student passionate about web development.',
            },
            {
                'username': 'student2',
                'email': 'student2@example.com',
                'first_name': 'Bob',
                'last_name': 'Williams',
                'bio': 'Learning Django and Python programming.',
            },
            {
                'username': 'student3',
                'email': 'student3@example.com',
                'first_name': 'Carol',
                'last_name': 'Brown',
                'bio': 'Interested in database design and backend development.',
            },
        ]

        for student_data in students_data:
            student, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'user_type': 'student',
                    'bio': student_data['bio'],
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                UserProfile.objects.create(user=student)
                self.stdout.write(f'Created student: {student.username}')

    def create_demo_courses(self):
        teacher = User.objects.get(username='teacher1')
        
        courses_data = [
            {
                'title': 'Introduction to Django',
                'description': 'Learn the basics of Django web framework, including models, views, templates, and forms.',
            },
            {
                'title': 'Advanced Web Development',
                'description': 'Advanced topics in web development including REST APIs, authentication, and deployment.',
            },
            {
                'title': 'Database Design',
                'description': 'Learn database design principles, normalization, and SQL optimization.',
            },
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                teacher=teacher,
                defaults={'description': course_data['description']}
            )
            if created:
                self.stdout.write(f'Created course: {course.title}')

        # Enroll students in courses
        students = User.objects.filter(user_type='student')
        courses = Course.objects.all()
        
        for student in students:
            for course in courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course
                )
                if created:
                    self.stdout.write(f'Enrolled {student.username} in {course.title}')

    def create_demo_chat_rooms(self):
        # Create general chat room
        general_room, created = ChatRoom.objects.get_or_create(
            name='general',
            defaults={'created_by': User.objects.get(username='teacher1')}
        )
        if created:
            # Add all users to general room
            for user in User.objects.all():
                general_room.participants.add(user)
            self.stdout.write('Created general chat room')

        # Create course-specific chat rooms
        courses = Course.objects.all()
        for course in courses:
            room_name = f'course-{course.id}'
            room, created = ChatRoom.objects.get_or_create(
                name=room_name,
                defaults={'created_by': course.teacher}
            )
            if created:
                # Add teacher and enrolled students
                room.participants.add(course.teacher)
                for student in course.students.all():
                    room.participants.add(student)
                self.stdout.write(f'Created chat room for {course.title}')

    def create_demo_status_updates(self):
        students = User.objects.filter(user_type='student')
        
        status_updates = [
            'Just finished the Django tutorial! Really excited to build my first web app.',
            'Working on my final project for the Advanced Web Development course.',
            'Database design is challenging but very interesting!',
            'Can\'t wait to start the next module on REST APIs.',
        ]

        for student in students:
            for i, status in enumerate(status_updates[:2]):  # Each student gets 2 status updates
                status_update, created = StatusUpdate.objects.get_or_create(
                    user=student,
                    content=status,
                    defaults={'created_at': timezone.now() - timedelta(days=i)}
                )
                if created:
                    self.stdout.write(f'Created status update for {student.username}')

    def create_demo_feedback(self):
        students = User.objects.filter(user_type='student')
        courses = Course.objects.all()

        feedback_data = [
            {'rating': 5, 'comment': 'Excellent course! The instructor explains everything clearly.'},
            {'rating': 4, 'comment': 'Great content and practical examples. Highly recommended!'},
            {'rating': 5, 'comment': 'Very comprehensive course with hands-on projects.'},
        ]

        for student in students:
            for course in courses:
                feedback, created = Feedback.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults=feedback_data[0]  # Use first feedback for all
                )
                if created:
                    self.stdout.write(f'Created feedback from {student.username} for {course.title}')
