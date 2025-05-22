from flask import Blueprint, request, jsonify
from src.models.models import db, WishlistItem, PriceHistory, Notification, User
from datetime import datetime

price_bp = Blueprint('price', __name__)

@price_bp.route('/update/<int:item_id>', methods=['POST'])
def update_price(item_id):
    """Update the price of a wishlist item and track history"""
    item = WishlistItem.query.get_or_404(item_id)
    data = request.get_json()
    
    if 'price' not in data:
        return jsonify({'error': 'Price is required'}), 400
    
    new_price = float(data['price'])
    old_price = item.current_price
    
    # Only update if price is different
    if old_price != new_price:
        # Create price history entry
        price_history = PriceHistory(
            price=new_price,
            item_id=item.id
        )
        db.session.add(price_history)
        
        # Update item price
        item.current_price = new_price
        
        # Update lowest and highest prices if needed
        if item.lowest_price is None or new_price < item.lowest_price:
            item.lowest_price = new_price
        
        if item.highest_price is None or new_price > item.highest_price:
            item.highest_price = new_price
        
        # Create notification if price dropped
        if old_price and new_price < old_price:
            drop_percentage = ((old_price - new_price) / old_price) * 100
            notification = Notification(
                type='price_drop',
                message=f"Price dropped by {drop_percentage:.2f}% on {item.name}",
                user_id=item.user_id,
                item_id=item.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Price updated successfully',
            'item': item.to_dict(),
            'price_history': price_history.to_dict()
        }), 200
    
    return jsonify({
        'message': 'Price unchanged',
        'item': item.to_dict()
    }), 200

@price_bp.route('/history/<int:item_id>', methods=['GET'])
def get_price_history(item_id):
    """Get price history for a specific item"""
    item = WishlistItem.query.get_or_404(item_id)
    
    # Get price history
    history = PriceHistory.query.filter_by(item_id=item_id).order_by(PriceHistory.recorded_at.desc()).all()
    
    return jsonify({
        'item': item.to_dict(),
        'price_history': [h.to_dict() for h in history]
    }), 200

@price_bp.route('/drops', methods=['GET'])
def get_price_drops():
    """Get all items with price drops for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get all items for user
    items = WishlistItem.query.filter_by(user_id=user_id).all()
    
    # Filter items with price drops
    price_drops = []
    for item in items:
        if item.has_price_drop():
            item_dict = item.to_dict()
            item_dict['price_drop_percentage'] = item.price_drop_percentage()
            price_drops.append(item_dict)
    
    return jsonify({
        'price_drops': price_drops
    }), 200

@price_bp.route('/simulate-drop/<int:item_id>', methods=['POST'])
def simulate_price_drop(item_id):
    """Simulate a price drop for testing purposes"""
    item = WishlistItem.query.get_or_404(item_id)
    data = request.get_json()
    
    drop_percentage = data.get('drop_percentage', 10)
    
    if not item.current_price:
        return jsonify({'error': 'Item has no current price'}), 400
    
    # Calculate new price with drop
    old_price = item.current_price
    new_price = old_price * (1 - (drop_percentage / 100))
    
    # Create price history entry
    price_history = PriceHistory(
        price=new_price,
        item_id=item.id
    )
    db.session.add(price_history)
    
    # Update item price
    item.current_price = new_price
    
    # Update lowest price if needed
    if item.lowest_price is None or new_price < item.lowest_price:
        item.lowest_price = new_price
    
    # Create notification
    notification = Notification(
        type='price_drop',
        message=f"Price dropped by {drop_percentage:.2f}% on {item.name}",
        user_id=item.user_id,
        item_id=item.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Price drop of {drop_percentage}% simulated successfully',
        'old_price': old_price,
        'new_price': new_price,
        'item': item.to_dict()
    }), 200
