from flask import Blueprint, request, jsonify
from src.models.models import db, WishlistItem, Category, User, PriceHistory
from datetime import datetime

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/', methods=['GET'])
def get_all_items():
    """Get all wishlist items for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get optional filters
    category_id = request.args.get('category_id')
    priority = request.args.get('priority')
    is_purchased = request.args.get('is_purchased')
    
    # Build query
    query = WishlistItem.query.filter_by(user_id=user_id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if priority is not None:
        query = query.filter_by(priority=int(priority))
    
    if is_purchased is not None:
        is_purchased_bool = is_purchased.lower() == 'true'
        query = query.filter_by(is_purchased=is_purchased_bool)
    
    # Execute query
    items = query.all()
    
    return jsonify({
        'items': [item.to_dict() for item in items]
    }), 200

@wishlist_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific wishlist item by ID"""
    item = WishlistItem.query.get_or_404(item_id)
    
    # Get price history
    price_history = PriceHistory.query.filter_by(item_id=item_id).order_by(PriceHistory.recorded_at.desc()).all()
    
    item_data = item.to_dict()
    item_data['price_history'] = [ph.to_dict() for ph in price_history]
    
    return jsonify({
        'item': item_data
    }), 200

@wishlist_bp.route('/', methods=['POST'])
def create_item():
    """Create a new wishlist item"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['name', 'user_id']):
        return jsonify({'error': 'Name and user_id are required'}), 400
    
    # Verify user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify category exists if provided
    category_id = data.get('category_id')
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
    
    # Create new item
    new_item = WishlistItem(
        name=data['name'],
        description=data.get('description', ''),
        url=data.get('url', ''),
        image_url=data.get('image_url', ''),
        current_price=data.get('current_price'),
        initial_price=data.get('current_price'),  # Set initial price same as current price
        lowest_price=data.get('current_price'),   # Set lowest price same as current price
        highest_price=data.get('current_price'),  # Set highest price same as current price
        priority=data.get('priority', 0),
        user_id=data['user_id'],
        category_id=category_id
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    # Add price history entry if price is provided
    if data.get('current_price'):
        price_history = PriceHistory(
            price=data['current_price'],
            item_id=new_item.id
        )
        db.session.add(price_history)
        db.session.commit()
    
    return jsonify({
        'message': 'Item added to wishlist successfully',
        'item': new_item.to_dict()
    }), 201

@wishlist_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an existing wishlist item"""
    item = WishlistItem.query.get_or_404(item_id)
    data = request.get_json()
    
    # Update item fields
    if 'name' in data:
        item.name = data['name']
    
    if 'description' in data:
        item.description = data['description']
    
    if 'url' in data:
        item.url = data['url']
    
    if 'image_url' in data:
        item.image_url = data['image_url']
    
    if 'priority' in data:
        item.priority = data['priority']
    
    if 'is_purchased' in data:
        item.is_purchased = data['is_purchased']
    
    if 'category_id' in data:
        # Verify category exists if provided
        category_id = data['category_id']
        if category_id:
            category = Category.query.get(category_id)
            if not category:
                return jsonify({'error': 'Category not found'}), 404
        item.category_id = category_id
    
    # Handle price update
    if 'current_price' in data and data['current_price'] is not None:
        old_price = item.current_price
        new_price = data['current_price']
        
        # Update price only if it's different
        if old_price != new_price:
            item.current_price = new_price
            
            # Update lowest and highest prices if needed
            if item.lowest_price is None or new_price < item.lowest_price:
                item.lowest_price = new_price
            
            if item.highest_price is None or new_price > item.highest_price:
                item.highest_price = new_price
            
            # Add price history entry
            price_history = PriceHistory(
                price=new_price,
                item_id=item.id
            )
            db.session.add(price_history)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item updated successfully',
        'item': item.to_dict()
    }), 200

@wishlist_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a wishlist item"""
    item = WishlistItem.query.get_or_404(item_id)
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({
        'message': 'Item deleted successfully'
    }), 200

@wishlist_bp.route('/price-drops', methods=['GET'])
def get_price_drops():
    """Get all items with price drops for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Get all items for user
    items = WishlistItem.query.filter_by(user_id=user_id).all()
    
    # Filter items with price drops
    price_drops = [item.to_dict() for item in items if item.has_price_drop()]
    
    # Add price drop percentage
    for item_dict in price_drops:
        item = next(item for item in items if item.id == item_dict['id'])
        item_dict['price_drop_percentage'] = item.price_drop_percentage()
    
    return jsonify({
        'price_drops': price_drops
    }), 200
