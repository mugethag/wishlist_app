import unittest
import json
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.models import db, User, Category, WishlistItem, PriceHistory, Coupon, Notification, CouponStatus

class WishlistAppTestCase(unittest.TestCase):
    """Test case for the wishlist app"""

    def setUp(self):
        """Set up test client and initialize database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='pbkdf2:sha256:150000$abc123'
            )
            db.session.add(test_user)
            
            # Create test categories
            categories = [
                Category(name='Electronics'),
                Category(name='Books')
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            self.test_user_id = test_user.id
            self.test_category_id = categories[0].id
    
    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(
            '/api/auth/register',
            json={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123'
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertEqual(data['user']['username'], 'newuser')
    
    def test_user_login(self):
        """Test user login endpoint"""
        # First register a user with a known password
        self.client.post(
            '/api/auth/register',
            json={
                'username': 'loginuser',
                'email': 'login@example.com',
                'password': 'password123'
            }
        )
        
        # Then try to login
        response = self.client.post(
            '/api/auth/login',
            json={
                'username': 'loginuser',
                'password': 'password123'
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Login successful')
    
    def test_category_endpoints(self):
        """Test category CRUD operations"""
        # Create category with unique name using UUID
        unique_name = f"Clothing-{uuid.uuid4()}"
        response = self.client.post(
            '/api/categories/',
            json={
                'name': unique_name,
                'description': 'Apparel and accessories'
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['category']['name'], unique_name)
        
        category_id = data['category']['id']
        
        # Get category
        response = self.client.get(f'/api/categories/{category_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['category']['name'], unique_name)
        
        # Update category
        response = self.client.put(
            f'/api/categories/{category_id}',
            json={
                'name': f"Fashion-{uuid.uuid4()}",
                'description': 'Fashion items and accessories'
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['category']['name'].startswith('Fashion-'))
        
        # Get all categories
        response = self.client.get('/api/categories/')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['categories']), 3)  # 2 from setup + 1 created
    
    def test_wishlist_item_endpoints(self):
        """Test wishlist item CRUD operations"""
        # Create item
        response = self.client.post(
            '/api/wishlist/',
            json={
                'name': 'Test Item',
                'description': 'A test item',
                'url': 'http://example.com/item',
                'current_price': 99.99,
                'priority': 1,
                'user_id': self.test_user_id,
                'category_id': self.test_category_id
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['item']['name'], 'Test Item')
        
        item_id = data['item']['id']
        
        # Get item
        response = self.client.get(f'/api/wishlist/{item_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['item']['name'], 'Test Item')
        self.assertEqual(data['item']['current_price'], 99.99)
        
        # Update item
        response = self.client.put(
            f'/api/wishlist/{item_id}',
            json={
                'name': 'Updated Item',
                'current_price': 89.99
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['item']['name'], 'Updated Item')
        self.assertEqual(data['item']['current_price'], 89.99)
        
        # Get all items for user
        response = self.client.get(f'/api/wishlist/?user_id={self.test_user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['items']), 1)
    
    def test_price_tracking(self):
        """Test price tracking and history"""
        # Create item with initial price
        response = self.client.post(
            '/api/wishlist/',
            json={
                'name': 'Price Test Item',
                'current_price': 100.00,
                'user_id': self.test_user_id
            }
        )
        data = json.loads(response.data)
        item_id = data['item']['id']
        
        # Update price
        response = self.client.post(
            f'/api/prices/update/{item_id}',
            json={
                'price': 90.00
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['item']['current_price'], 90.00)
        
        # Get price history
        response = self.client.get(f'/api/prices/history/{item_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['price_history']), 1)
        
        # Simulate price drop
        response = self.client.post(
            f'/api/prices/simulate-drop/{item_id}',
            json={
                'drop_percentage': 20
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(data['new_price'], data['old_price'])
        
        # Check price drops for user
        response = self.client.get(f'/api/prices/drops?user_id={self.test_user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['price_drops']), 1)
    
    def test_coupon_endpoints(self):
        """Test coupon CRUD operations"""
        # Create item first
        response = self.client.post(
            '/api/wishlist/',
            json={
                'name': 'Coupon Test Item',
                'current_price': 100.00,
                'user_id': self.test_user_id
            }
        )
        data = json.loads(response.data)
        item_id = data['item']['id']
        
        # Create coupon
        response = self.client.post(
            '/api/coupons/',
            json={
                'code': 'TEST20',
                'description': '20% off',
                'discount_amount': 20,
                'is_percentage': True,
                'item_id': item_id
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['coupon']['code'], 'TEST20')
        
        coupon_id = data['coupon']['id']
        
        # Get coupon
        response = self.client.get(f'/api/coupons/{coupon_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['coupon']['code'], 'TEST20')
        
        # Update coupon
        response = self.client.put(
            f'/api/coupons/{coupon_id}',
            json={
                'code': 'UPDATED30',
                'discount_amount': 30
            }
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['coupon']['code'], 'UPDATED30')
        self.assertEqual(data['coupon']['discount_amount'], 30)
        
        # Get all coupons for item
        response = self.client.get(f'/api/coupons/?item_id={item_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['coupons']), 1)
        
        # Get all coupons for user
        response = self.client.get(f'/api/coupons/?user_id={self.test_user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['coupons']), 1)
    
    def test_notification_endpoints(self):
        """Test notification endpoints"""
        # Create item first
        response = self.client.post(
            '/api/wishlist/',
            json={
                'name': 'Notification Test Item',
                'current_price': 100.00,
                'user_id': self.test_user_id
            }
        )
        data = json.loads(response.data)
        item_id = data['item']['id']
        
        # Create a notification manually
        with app.app_context():
            notification = Notification(
                type='test',
                message='Test notification',
                user_id=self.test_user_id,
                item_id=item_id
            )
            db.session.add(notification)
            db.session.commit()
            notification_id = notification.id
        
        # Get notifications for user
        response = self.client.get(f'/api/notifications/?user_id={self.test_user_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['notifications']), 1)
        
        # Mark notification as read
        response = self.client.put(f'/api/notifications/{notification_id}/read')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['notification']['is_read'], True)
        
        # Mark all as read
        response = self.client.put(f'/api/notifications/read-all?user_id={self.test_user_id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Get only unread notifications (should be empty now)
        response = self.client.get(f'/api/notifications/?user_id={self.test_user_id}&unread_only=true')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['notifications']), 0)

if __name__ == '__main__':
    unittest.main()
