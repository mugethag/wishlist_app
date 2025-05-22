from flask import Blueprint, request, jsonify
from src.models.models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def get_all_users():
    """Get all users (admin only in a real app)"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update user fields
    if 'username' in data:
        # Check if username already exists
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Username already exists'}), 409
        user.username = data['username']
    
    if 'email' in data:
        # Check if email already exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already exists'}), 409
        user.email = data['email']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User deleted successfully'
    }), 200
