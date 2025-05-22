from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.models import db, User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    # Check if user exists and password is correct
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Return user data (in a real app, you would generate a JWT token here)
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # In a real app with JWT, you would invalidate the token here
    return jsonify({'message': 'Logout successful'}), 200
