from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wishlists = db.relationship('WishlistItem', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    
    # Relationships
    items = db.relationship('WishlistItem', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    current_price = db.Column(db.Float)
    initial_price = db.Column(db.Float)
    lowest_price = db.Column(db.Float)
    highest_price = db.Column(db.Float)
    priority = db.Column(db.Integer, default=0)  # 0=low, 1=medium, 2=high
    is_purchased = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='item', lazy=True, cascade="all, delete-orphan")
    coupons = db.relationship('Coupon', backref='item', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<WishlistItem {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'current_price': self.current_price,
            'initial_price': self.initial_price,
            'lowest_price': self.lowest_price,
            'highest_price': self.highest_price,
            'priority': self.priority,
            'is_purchased': self.is_purchased,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id,
            'category_id': self.category_id
        }
    
    def has_price_drop(self):
        """Check if the current price is lower than the initial price"""
        if self.current_price and self.initial_price:
            return self.current_price < self.initial_price
        return False
    
    def price_drop_percentage(self):
        """Calculate the percentage of price drop"""
        if self.current_price and self.initial_price and self.initial_price > 0:
            return ((self.initial_price - self.current_price) / self.initial_price) * 100
        return 0

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'), nullable=False)
    
    def __repr__(self):
        return f'<PriceHistory {self.price} at {self.recorded_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'recorded_at': self.recorded_at,
            'item_id': self.item_id
        }

class CouponStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100))
    description = db.Column(db.String(255))
    discount_amount = db.Column(db.Float)  # Either fixed amount or percentage
    is_percentage = db.Column(db.Boolean, default=True)  # True if discount is percentage, False if fixed amount
    status = db.Column(db.Enum(CouponStatus), default=CouponStatus.ACTIVE)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'), nullable=False)
    
    def __repr__(self):
        return f'<Coupon {self.code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'discount_amount': self.discount_amount,
            'is_percentage': self.is_percentage,
            'status': self.status.value,
            'valid_from': self.valid_from,
            'valid_until': self.valid_until,
            'created_at': self.created_at,
            'item_id': self.item_id
        }
    
    def is_active(self):
        """Check if the coupon is currently active"""
        now = datetime.utcnow()
        return (self.status == CouponStatus.ACTIVE and 
                self.valid_from <= now and 
                (self.valid_until is None or self.valid_until >= now))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'price_drop', 'coupon', etc.
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    item = db.relationship('WishlistItem')
    
    def __repr__(self):
        return f'<Notification {self.type} for {self.item_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at,
            'user_id': self.user_id,
            'item_id': self.item_id
        }
