from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from .models import Course, CourseMaterial, Enrollment, Assignment, Feedback
from users.models import UserProfile

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        self.student_profile = UserProfile.objects.create(user=self.student)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.description, 'This is a test course description')
        self.assertEqual(self.course.teacher, self.teacher)
        self.assertTrue(self.course.is_active)
        self.assertIsNotNone(self.course.created_at)
        self.assertIsNotNone(self.course.updated_at)

    def test_course_string_representation(self):
        self.assertEqual(str(self.course), 'Test Course')

    def test_course_get_student_count(self):
        self.assertEqual(self.course.get_student_count(), 0)
        
        # Enroll a student
        Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(self.course.get_student_count(), 1)


class CourseMaterialModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_course_material_creation(self):
        # Create a simple file for testing
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')
        
        material = CourseMaterial.objects.create(
            course=self.course,
            title='Test Material',
            description='This is a test material',
            file=uploaded_file,
            material_type='pdf'
        )
        
        self.assertEqual(material.title, 'Test Material')
        self.assertEqual(material.description, 'This is a test material')
        self.assertEqual(material.course, self.course)
        self.assertEqual(material.material_type, 'pdf')
        self.assertIsNotNone(material.uploaded_at)

    def test_course_material_string_representation(self):
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')
        
        material = CourseMaterial.objects.create(
            course=self.course,
            title='Test Material',
            description='This is a test material',
            file=uploaded_file,
            material_type='pdf'
        )
        
        expected_string = f"Test Material - {self.course.title}"
        self.assertEqual(str(material), expected_string)


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        self.student_profile = UserProfile.objects.create(user=self.student)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertIsNotNone(enrollment.enrolled_at)

    def test_enrollment_string_representation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        expected_string = f"{self.student.username} enrolled in {self.course.title}"
        self.assertEqual(str(enrollment), expected_string)

    def test_enrollment_unique_constraint(self):
        # Create first enrollment
        Enrollment.objects.create(student=self.student, course=self.course)
        
        # Try to create duplicate enrollment
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Enrollment.objects.create(student=self.student, course=self.course)


class AssignmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_assignment_creation(self):
        due_date = timezone.now() + timedelta(days=7)
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='This is a test assignment',
            due_date=due_date
        )
        
        self.assertEqual(assignment.title, 'Test Assignment')
        self.assertEqual(assignment.description, 'This is a test assignment')
        self.assertEqual(assignment.course, self.course)
        self.assertEqual(assignment.due_date, due_date)
        self.assertIsNotNone(assignment.created_at)

    def test_assignment_string_representation(self):
        due_date = timezone.now() + timedelta(days=7)
        assignment = Assignment.objects.create(
            course=self.course,
            title='Test Assignment',
            description='This is a test assignment',
            due_date=due_date
        )
        
        expected_string = f"Test Assignment - {self.course.title}"
        self.assertEqual(str(assignment), expected_string)

    def test_assignment_is_overdue(self):
        # Create assignment with past due date
        past_due_date = timezone.now() - timedelta(days=1)
        overdue_assignment = Assignment.objects.create(
            course=self.course,
            title='Overdue Assignment',
            description='This assignment is overdue',
            due_date=past_due_date
        )
        
        # Create assignment with future due date
        future_due_date = timezone.now() + timedelta(days=1)
        active_assignment = Assignment.objects.create(
            course=self.course,
            title='Active Assignment',
            description='This assignment is active',
            due_date=future_due_date
        )
        
        self.assertTrue(overdue_assignment.is_overdue())
        self.assertFalse(active_assignment.is_overdue())


class FeedbackModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        self.student_profile = UserProfile.objects.create(user=self.student)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_feedback_creation(self):
        feedback = Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment='This is a great course!'
        )
        
        self.assertEqual(feedback.student, self.student)
        self.assertEqual(feedback.course, self.course)
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, 'This is a great course!')
        self.assertIsNotNone(feedback.created_at)

    def test_feedback_string_representation(self):
        feedback = Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment='This is a great course!'
        )
        
        expected_string = f"Feedback by {self.student.username} for {self.course.title}"
        self.assertEqual(str(feedback), expected_string)

    def test_feedback_unique_constraint(self):
        # Create first feedback
        Feedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment='First feedback'
        )
        
        # Try to create duplicate feedback
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Feedback.objects.create(
                student=self.student,
                course=self.course,
                rating=4,
                comment='Second feedback'
            )


class CourseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        self.student_profile = UserProfile.objects.create(user=self.student)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_course_list_page(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')

    def test_course_detail_page(self):
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')

    def test_course_detail_page_not_found(self):
        response = self.client.get(reverse('course_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_create_course_page_teacher_only(self):
        # Student should be redirected
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Teacher should have access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Course')

    def test_create_course_post_success(self):
        self.client.login(username='testteacher', password='testpass123')
        data = {
            'title': 'New Course',
            'description': 'This is a new course'
        }
        response = self.client.post(reverse('create_course'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Course.objects.filter(title='New Course').exists())

    def test_enroll_course_student_only(self):
        # Teacher should be redirected
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Student should be able to enroll
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after enrollment
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())

    def test_leave_course_student_only(self):
        # Create enrollment first
        Enrollment.objects.create(student=self.student, course=self.course)
        
        # Teacher should be redirected
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('leave_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Student should be able to leave
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('leave_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after leaving
        self.assertFalse(Enrollment.objects.filter(student=self.student, course=self.course).exists())

    def test_upload_material_page_teacher_only(self):
        # Student should be redirected
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('upload_material', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Teacher should have access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('upload_material', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Course Material')

    def test_leave_feedback_page_student_only(self):
        # Create enrollment first
        Enrollment.objects.create(student=self.student, course=self.course)
        
        # Teacher should be redirected
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('leave_feedback', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Student should have access
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('leave_feedback', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Share Your Experience')

    def test_course_students_page_teacher_only(self):
        # Student should be redirected
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('course_students', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Teacher should have access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('course_students', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Course Students')


class CourseIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)
        self.student_profile = UserProfile.objects.create(user=self.student)
        
        self.course = Course.objects.create(
            title='Test Course',
            description='This is a test course description',
            teacher=self.teacher
        )

    def test_full_course_workflow(self):
        # 1. Teacher creates course (already done in setUp)
        self.assertEqual(Course.objects.count(), 1)
        
        # 2. Student enrolls in course
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.get_student_count(), 1)
        
        # 3. Teacher uploads material
        self.client.login(username='testteacher', password='testpass123')
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')
        
        data = {
            'title': 'Test Material',
            'description': 'This is a test material',
            'file': uploaded_file,
            'material_type': 'pdf'
        }
        response = self.client.post(reverse('upload_material', args=[self.course.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.materials.count(), 1)
        
        # 4. Student leaves feedback
        self.client.login(username='teststudent', password='testpass123')
        data = {
            'rating': 5,
            'comment': 'This is a great course!'
        }
        response = self.client.post(reverse('leave_feedback', args=[self.course.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.feedback.count(), 1)
        
        # 5. Student leaves course
        response = self.client.get(reverse('leave_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.get_student_count(), 0)
