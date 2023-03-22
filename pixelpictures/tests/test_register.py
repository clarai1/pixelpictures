from django.test import TestCase, Client
from django.db import IntegrityError
from django.urls import reverse
import unittest
from http import HTTPStatus

from pixelpictures.models import User
from pixelpictures.forms import RegisterUserForm     

# Login/register/logout tests

class UserTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='User1', email='user1@example.com', password='pssSre!1')
        self.user1.save()
    
    # Database tests

    def test_unique_username_database(self):
        try:
            User.objects.create(username='User1', email='user2@example.com', password='passSre!1')
            self.fail("Two users with same username")
        except IntegrityError:
            pass
    
    def test_unique_email_database(self):
        try:
            User.objects.create(username='User2', email='user1@example.com', password='passSre!1')
            self.fail("Two users with same email")
        except IntegrityError:
            pass

    # Register form tests

    def test_register_unique_username(self):
        response = self.client.post('/register', data={
            'username': 'User1',
            'email': 'someEmail@example.com',
            'password1': 'somePass123',
            'password2': 'somePass123'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>A user with that username already exists.</li>', html=True)

    def test_register_no_username(self):
        response = self.client.post('/register', data={
            'username': '',
            'email': 'user2@example.com',
            'password1': 'somePass123',
            'password2': 'somePass123'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>This field is required.</li>', html=True)

    def test_register_unique_email(self):
        response = self.client.post('/register', data={
            'username': 'User2',
            'email': 'user1@example.com',
            'password1': 'somePass123',
            'password2': 'somePass123'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>Email already exists.</li>', html=True)

    def test_register_no_email(self):
        response = self.client.post('/register', data={
            'username': 'User2',
            'email': '',
            'password1': 'somePass123',
            'password2': 'somePass123'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>This field is required.</li>', html=True)

    def test_register_no_password(self):
        response = self.client.post('/register', data={
            'username': 'User2',
            'email': 'user2@example.com',
            'password1': '',
            'password2': 'somePass123'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>This field is required.</li>', html=True)

    def test_register_wrong_password2(self):
        response = self.client.post('/register', data={
            'username': 'User2',
            'email': 'user2@example.com',
            'password1': 'somePass123',
            'password2': 'somePass'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.request["PATH_INFO"], '/register')
        self.assertContains(response, '<li>The two password fields didn’t match.</li>', html=True)

    # Login tests

    def test_login_and_logout(self):
        response = self.client.post('/login', data={
            'username': 'User1',
            'password': 'pssSre!1'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(response.wsgi_request.user, self.user1)
        response = self.client.get('/logout')
        self.assertNotEqual(response.wsgi_request.user, self.user1)
        self.assertRedirects(response, reverse('index'))

    def test_login_wrong_username(self):
        response = self.client.post('/login', data={
            'username': 'User2',
            'password': 'somePass123'
        })
        self.assertEqual(response.request["PATH_INFO"], '/login')
        self.assertContains(response, 'Incorrect username or password.')

    def test_login_wrong_password(self):
        response = self.client.post('/login', data={
            'username': 'User1',
            'password': 'wrongPass123'
        })
        self.assertEqual(response.request["PATH_INFO"], '/login')
        self.assertContains(response, 'Incorrect username or password.')
