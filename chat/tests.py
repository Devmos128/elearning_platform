from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import ChatRoom, Message

User = get_user_model()


class ChatRoomModelTest(TestCase):
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

    def test_chat_room_creation(self):
        chat_room = ChatRoom.objects.create(
            name='Test Chat Room',
            created_by=self.teacher
        )
        
        self.assertEqual(chat_room.name, 'Test Chat Room')
        self.assertEqual(chat_room.created_by, self.teacher)
        self.assertIsNotNone(chat_room.created_at)

    def test_chat_room_string_representation(self):
        chat_room = ChatRoom.objects.create(
            name='Test Chat Room',
            created_by=self.teacher
        )
        
        self.assertEqual(str(chat_room), 'Test Chat Room')

    def test_chat_room_participants(self):
        chat_room = ChatRoom.objects.create(
            name='Test Chat Room',
            created_by=self.teacher
        )
        
        # Add participants
        chat_room.participants.add(self.teacher, self.student)
        
        self.assertEqual(chat_room.participants.count(), 2)
        self.assertIn(self.teacher, chat_room.participants.all())
        self.assertIn(self.student, chat_room.participants.all())


class MessageModelTest(TestCase):
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
        
        self.chat_room = ChatRoom.objects.create(
            name='Test Chat Room',
            created_by=self.teacher
        )

    def test_message_creation(self):
        message = Message.objects.create(
            room=self.chat_room,
            sender=self.teacher,
            content='Hello, this is a test message!'
        )
        
        self.assertEqual(message.room, self.chat_room)
        self.assertEqual(message.sender, self.teacher)
        self.assertEqual(message.content, 'Hello, this is a test message!')
        self.assertIsNotNone(message.timestamp)

    def test_message_string_representation(self):
        message = Message.objects.create(
            room=self.chat_room,
            sender=self.teacher,
            content='Test message'
        )
        
        expected_string = f"Message-{message.id}-{self.teacher.username}"
        self.assertEqual(str(message), expected_string)

    def test_message_ordering(self):
        # Create messages in reverse order
        message2 = Message.objects.create(
            room=self.chat_room,
            sender=self.student,
            content='Second message'
        )
        message1 = Message.objects.create(
            room=self.chat_room,
            sender=self.teacher,
            content='First message'
        )
        
        messages = Message.objects.all()
        self.assertEqual(messages[0], message1)  # First by timestamp
        self.assertEqual(messages[1], message2)  # Second by timestamp

    def test_chat_room_messages_relationship(self):
        message1 = Message.objects.create(
            room=self.chat_room,
            sender=self.teacher,
            content='First message'
        )
        message2 = Message.objects.create(
            room=self.chat_room,
            sender=self.student,
            content='Second message'
        )
        
        self.assertEqual(self.chat_room.messages.count(), 2)
        self.assertIn(message1, self.chat_room.messages.all())
        self.assertIn(message2, self.chat_room.messages.all())


class ChatViewsTest(TestCase):
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
        
        self.chat_room = ChatRoom.objects.create(
            name='Test Chat Room',
            created_by=self.teacher
        )

    def test_chat_list_page_requires_login(self):
        # Not logged in should be redirected
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_chat_list_page_when_logged_in(self):
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chat Rooms')

    def test_create_chat_room_page_requires_login(self):
        # Not logged in should be redirected
        response = self.client.get(reverse('create_chat_room'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_chat_room_page_when_logged_in(self):
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('create_chat_room'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Chat Room')

    def test_create_chat_room_post_success(self):
        self.client.login(username='testteacher', password='testpass123')
        data = {
            'name': 'New Chat Room'
        }
        response = self.client.post(reverse('create_chat_room'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(ChatRoom.objects.filter(name='New Chat Room').exists())

    def test_chat_room_page_requires_login(self):
        # Not logged in should be redirected
        response = self.client.get(reverse('chat_room', args=['Test Chat Room']))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_chat_room_page_when_logged_in(self):
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('chat_room', args=['Test Chat Room']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Chat Room')

    def test_chat_room_page_not_found(self):
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('chat_room', args=['NonExistentRoom']))
        self.assertEqual(response.status_code, 404)

    def test_chat_room_with_spaces_in_name(self):
        self.client.login(username='testteacher', password='testpass123')
        room_with_spaces = ChatRoom.objects.create(
            name='Room With Spaces',
            created_by=self.teacher
        )
        response = self.client.get(reverse('chat_room', args=['Room With Spaces']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Room With Spaces')


class ChatIntegrationTest(TestCase):
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

    def test_full_chat_workflow(self):
        # 1. Teacher creates chat room
        self.client.login(username='testteacher', password='testpass123')
        data = {
            'name': 'Study Group'
        }
        response = self.client.post(reverse('create_chat_room'), data)
        self.assertEqual(response.status_code, 302)
        
        chat_room = ChatRoom.objects.get(name='Study Group')
        self.assertEqual(chat_room.created_by, self.teacher)
        
        # 2. Teacher accesses chat room
        response = self.client.get(reverse('chat_room', args=['Study Group']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Group')
        
        # 3. Student can also access the chat room
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('chat_room', args=['Study Group']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study Group')
        
        # 4. Messages can be created (this would normally be done via WebSocket)
        message = Message.objects.create(
            room=chat_room,
            sender=self.teacher,
            content='Hello everyone!'
        )
        self.assertEqual(message.room, chat_room)
        self.assertEqual(message.sender, self.teacher)
        self.assertEqual(message.content, 'Hello everyone!')


class ChatModelRelationshipsTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='testpass123',
            user_type='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='testpass123',
            user_type='student'
        )

    def test_user_chat_rooms_relationship(self):
        # Create chat rooms
        room1 = ChatRoom.objects.create(name='Room 1', created_by=self.teacher)
        room2 = ChatRoom.objects.create(name='Room 2', created_by=self.teacher)
        
        # Add participants
        room1.participants.add(self.teacher, self.student1)
        room2.participants.add(self.teacher, self.student1, self.student2)
        
        # Test user's chat rooms
        self.assertEqual(self.teacher.chat_rooms.count(), 2)
        self.assertEqual(self.student1.chat_rooms.count(), 2)
        self.assertEqual(self.student2.chat_rooms.count(), 1)

    def test_chat_room_messages_ordering(self):
        room = ChatRoom.objects.create(name='Test Room', created_by=self.teacher)
        
        # Create messages
        message1 = Message.objects.create(
            room=room,
            sender=self.teacher,
            content='First message'
        )
        message2 = Message.objects.create(
            room=room,
            sender=self.student1,
            content='Second message'
        )
        message3 = Message.objects.create(
            room=room,
            sender=self.student2,
            content='Third message'
        )
        
        # Test ordering (by timestamp)
        messages = room.messages.all()
        self.assertEqual(messages[0], message1)
        self.assertEqual(messages[1], message2)
        self.assertEqual(messages[2], message3)

    def test_chat_room_participants_management(self):
        room = ChatRoom.objects.create(name='Test Room', created_by=self.teacher)
        
        # Initially only creator is participant
        self.assertEqual(room.participants.count(), 0)
        
        # Add participants
        room.participants.add(self.student1, self.student2)
        self.assertEqual(room.participants.count(), 2)
        
        # Remove a participant
        room.participants.remove(self.student1)
        self.assertEqual(room.participants.count(), 1)
        self.assertIn(self.student2, room.participants.all())
        self.assertNotIn(self.student1, room.participants.all())


class ChatSecurityTest(TestCase):
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
        
        self.chat_room = ChatRoom.objects.create(
            name='Private Room',
            created_by=self.teacher
        )

    def test_chat_room_access_control(self):
        # Both users should be able to access any chat room
        # (In a real application, you might want to restrict access)
        
        # Teacher access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('chat_room', args=['Private Room']))
        self.assertEqual(response.status_code, 200)
        
        # Student access
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('chat_room', args=['Private Room']))
        self.assertEqual(response.status_code, 200)

    def test_message_sender_integrity(self):
        # Test that messages are properly associated with their senders
        message = Message.objects.create(
            room=self.chat_room,
            sender=self.teacher,
            content='Test message'
        )
        
        self.assertEqual(message.sender, self.teacher)
        self.assertNotEqual(message.sender, self.student)
        
        # Test that we can't create a message without a sender
        with self.assertRaises(Exception):
            Message.objects.create(
                room=self.chat_room,
                content='Message without sender'
            )
