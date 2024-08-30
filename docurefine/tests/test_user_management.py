import unittest
from flask_testing import TestCase
from src.app import app, db
from src.user_management import User
import os

class TestUserManagement(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_registration(self):
        response = self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        ), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Registration successful', response.data)

    def test_user_login_logout(self):
        # Register a user
        self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        ))

        # Login
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Upload', response.data)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Login', response.data)

    def test_file_management(self):
        # Register and login
        self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        ))
        self.client.post('/login', data=dict(
            username='testuser',
            password='testpassword'
        ))

        # Create a test file
        test_file_path = os.path.join(app.config['OUTPUT_FOLDER'], '1', 'test_file.txt')
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write('Test content')

        # List files
        response = self.client.get('/files')
        self.assert200(response)
        self.assertIn(b'test_file.txt', response.data)

        # Delete file
        response = self.client.get('/delete/test_file.txt', follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'File test_file.txt has been deleted', response.data)

if __name__ == '__main__':
    unittest.main()