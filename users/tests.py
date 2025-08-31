from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import StatusUpdate, UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        # Create UserProfile objects manually since they're not auto-created
        self.student_profile = UserProfile.objects.create(user=self.student)
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)

    def test_user_creation(self):
        self.assertEqual(self.student.username, 'teststudent')
        self.assertEqual(self.student.user_type, 'student')
        self.assertTrue(self.student.is_student())
        self.assertFalse(self.student.is_teacher())

        self.assertEqual(self.teacher.username, 'testteacher')
        self.assertEqual(self.teacher.user_type, 'teacher')
        self.assertTrue(self.teacher.is_teacher())
        self.assertFalse(self.teacher.is_student())

    def test_user_profile_creation(self):
        profile = UserProfile.objects.get(user=self.student)
        self.assertEqual(profile.user, self.student)
        self.assertEqual(str(profile), f"{self.student.username}'s Profile")

    def test_status_update_creation(self):
        status = StatusUpdate.objects.create(
            user=self.student,
            content='Test status update'
        )
        self.assertEqual(status.user, self.student)
        self.assertEqual(status.content, 'Test status update')
        self.assertIn('Test status update', str(status))

    def test_user_string_representation(self):
        self.assertIn('teststudent', str(self.student))
        self.assertIn('Student', str(self.student))
        self.assertIn('testteacher', str(self.teacher))
        self.assertIn('Teacher', str(self.teacher))

    def test_user_methods(self):
        self.assertTrue(self.student.is_student())
        self.assertFalse(self.student.is_teacher())
        self.assertTrue(self.teacher.is_teacher())
        self.assertFalse(self.teacher.is_student())


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        # Create UserProfile objects
        self.student_profile = UserProfile.objects.create(user=self.student)
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)

    def test_home_page_redirect_when_not_logged_in(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_page_when_logged_in(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'teststudent')

    def test_register_page_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Your Account')

    def test_register_page_post_success(self):
        data = {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'student'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_page_post_success(self):
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_login_page_post_failure(self):
        data = {
            'username': 'teststudent',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Login')

    def test_user_profile_page(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('user_profile', args=['teststudent']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'teststudent')

    def test_user_profile_page_not_found(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('user_profile', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)

    def test_search_users_teacher_only(self):
        # Student should be redirected
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('search_users'))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Teacher should have access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('search_users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Users')

    def test_search_users_post(self):
        self.client.login(username='testteacher', password='testpass123')
        data = {'query': 'test'}
        response = self.client.post(reverse('search_users'), data)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        # Create UserProfile objects
        self.student_profile = UserProfile.objects.create(user=self.student)
        self.teacher_profile = UserProfile.objects.create(user=self.teacher)

    def test_user_list_api_requires_auth(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 403)  # Forbidden (Django REST Framework default)

    def test_user_list_api_with_auth(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'teststudent')

    def test_user_detail_api(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(f'/api/users/{self.student.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'teststudent')

    def test_user_detail_api_not_found(self):
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get('/api/users/999/')
        self.assertEqual(response.status_code, 404)


class StatusUpdateTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.profile = UserProfile.objects.create(user=self.student)

    def test_status_update_creation(self):
        status = StatusUpdate.objects.create(
            user=self.student,
            content='This is a test status update'
        )
        self.assertEqual(status.user, self.student)
        self.assertEqual(status.content, 'This is a test status update')
        self.assertIsNotNone(status.created_at)
        self.assertIsNotNone(status.updated_at)

    def test_status_update_string_representation(self):
        status = StatusUpdate.objects.create(
            user=self.student,
            content='Short status'
        )
        self.assertIn('teststudent', str(status))
        self.assertIn('Short status', str(status))

    def test_status_update_ordering(self):
        status1 = StatusUpdate.objects.create(
            user=self.student,
            content='First status'
        )
        status2 = StatusUpdate.objects.create(
            user=self.student,
            content='Second status'
        )
        statuses = StatusUpdate.objects.all()
        self.assertEqual(statuses[0], status2)  # Most recent first
        self.assertEqual(statuses[1], status1)


class UserProfileTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )
        self.profile = UserProfile.objects.create(user=self.student)

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.user, self.student)
        self.assertEqual(str(self.profile), f"{self.student.username}'s Profile")

    def test_user_profile_courses_enrolled(self):
        # This will be tested more thoroughly when we have Course model tests
        self.assertEqual(self.profile.courses_enrolled.count(), 0)

    def test_user_profile_upcoming_deadlines(self):
        # This will be tested more thoroughly when we have Assignment model tests
        self.assertEqual(self.profile.upcoming_deadlines.count(), 0)
