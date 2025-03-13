import unittest
import os
import tempfile
import json
from app import app, db
from models import User, Palette

class AuthAndPaletteTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test environment before each test."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()  # Drop all tables first
            db.create_all()  # Then create them again
    
    def tearDown(self):
        """Clean up after each test."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def register(self, username, email, password, confirm_password):
        """Helper method to register a user."""
        return self.client.post('/register', data=dict(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        ), follow_redirects=True)
    
    def login(self, email, password):
        """Helper method to login a user."""
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        """Helper method to logout a user."""
        return self.client.get('/logout', follow_redirects=True)
    
    def test_register_and_login(self):
        """Test user registration and login."""
        # Test registration
        response = self.register('testuser', 'test@example.com', 'password123', 'password123')
        self.assertIn(b'Account created successfully', response.data)
        
        # Test login with correct credentials
        response = self.login('test@example.com', 'password123')
        self.assertIn(b'Logged in successfully', response.data)
        
        # Test logout
        response = self.logout()
        self.assertIn(b'Logged out successfully', response.data)
        
        # Test login with incorrect password
        response = self.login('test@example.com', 'wrongpassword')
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_save_palette(self):
        """Test saving a color palette."""
        # Register and login
        self.register('user2', 'user2@example.com', 'password123', 'password123')
        self.login('user2@example.com', 'password123')
        
        # Save a palette
        response = self.client.post('/save_palette', data=dict(
            name='Test Palette',
            colors=json.dumps(['#FF5733', '#33FF57', '#3357FF'])
        ))
        self.assertEqual(response.status_code, 200)
        
        # Check if palette appears in my palettes page
        response = self.client.get('/my_palettes')
        self.assertIn(b'Test Palette', response.data)
        self.assertIn(b'#FF5733', response.data)
    
    def test_delete_palette(self):
        """Test deleting a color palette."""
        # Register, login and save a palette
        self.register('user3', 'user3@example.com', 'password123', 'password123')
        self.login('user3@example.com', 'password123')
        
        # Save a palette
        self.client.post('/save_palette', data=dict(
            name='Test Palette',
            colors=json.dumps(['#FF5733', '#33FF57', '#3357FF'])
        ))
        
        # Get the palette ID
        with app.app_context():
            palette = Palette.query.filter_by(name='Test Palette').first()
            palette_id = palette.id
        
        # Delete the palette
        response = self.client.post(f'/delete_palette/{palette_id}', follow_redirects=True)
        self.assertIn(b'Palette deleted successfully', response.data)
        
        # Check if palette is removed from my palettes page
        response = self.client.get('/my_palettes')
        self.assertNotIn(b'Test Palette', response.data)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected routes."""
        # Try to access my palettes without login
        response = self.client.get('/my_palettes', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)
        
        # Try to save a palette without login
        response = self.client.post('/save_palette', data=dict(
            name='Test Palette',
            colors=json.dumps(['#FF5733', '#33FF57', '#3357FF'])
        ), follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

if __name__ == '__main__':
    unittest.main() 