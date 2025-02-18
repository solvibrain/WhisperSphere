from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Topic, Room, Message
from .forms import RoomForm, UserForm, MyUserCreationForm

User = get_user_model()

class UserModelTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_profile_methods(self):
        user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.get_full_name(), 'John Doe')
        self.assertEqual(user.get_short_name(), 'John')

class RoomModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='host@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Test Topic')

    def test_room_creation(self):
        room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room',
            description='Test Description'
        )
        self.assertEqual(room.name, 'Test Room')
        self.assertEqual(room.host, self.user)
        self.assertEqual(room.topic, self.topic)
        self.assertEqual(room.participants.count(), 0)

class MessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room'
        )

    def test_message_creation(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='Test Message'
        )
        self.assertEqual(message.body, 'Test Message')
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.room, self.room)

class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

class RoomViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='host@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room'
        )
        self.client.login(email='host@example.com', password='testpass123')

    def test_create_room_view(self):
        response = self.client.post(reverse('create-room'), {
            'name': 'New Room',
            'topic': 'New Topic',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name='New Room').exists())

    def test_delete_room_view(self):
        response = self.client.post(reverse('delete-room', args=[self.room.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(id=self.room.id).exists())

class FormTests(TestCase):
    def test_room_form_valid(self):
        form_data = {
            'name': 'Test Room',
            'description': 'Test Description'
        }
        form = RoomForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_valid(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com'
        }
        form = UserForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())

    def test_user_creation_form_valid(self):
        form_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = MyUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
