from flask import Blueprint, request, jsonify
from src.models.models import db, Notification, User, WishlistItem

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/', methods=['GET'])
def get_notifications():
    """Get all notifications for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get optional filters
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notification_type = request.args.get('type')
    
    # Build query
    query = Notification.query.filter_by(user_id=user_id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    if notification_type:
        query = query.filter_by(type=notification_type)
    
    # Execute query with ordering by most recent first
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    # Prepare response with item details
    result = []
    for notification in notifications:
        notif_dict = notification.to_dict()
        item = WishlistItem.query.get(notification.item_id)
        if item:
            notif_dict['item_name'] = item.name
            notif_dict['item_image'] = item.image_url
        result.append(notif_dict)
    
    return jsonify({
        'notifications': result
    }), 200

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark a notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200

@notification_bp.route('/read-all', methods=['PUT'])
def mark_all_as_read():
    """Mark all notifications as read for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Update all unread notifications for the user
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({
        'message': f'Marked {len(notifications)} notifications as read'
    }), 200

@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Notification deleted successfully'
    }), 200
