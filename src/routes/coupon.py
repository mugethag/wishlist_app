from flask import Blueprint, request, jsonify
from src.models.models import db, Coupon, WishlistItem, Notification, User, CouponStatus
from datetime import datetime

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/', methods=['GET'])
def get_all_coupons():
    """Get all coupons for a specific item or user"""
    item_id = request.args.get('item_id')
    user_id = request.args.get('user_id')
    
    if item_id:
        # Get coupons for specific item
        coupons = Coupon.query.filter_by(item_id=item_id).all()
    elif user_id:
        # Get coupons for all items of a user
        items = WishlistItem.query.filter_by(user_id=user_id).all()
        item_ids = [item.id for item in items]
        coupons = Coupon.query.filter(Coupon.item_id.in_(item_ids)).all()
    else:
        return jsonify({'error': 'Either item_id or user_id is required'}), 400
    
    # Filter active coupons if requested
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    if active_only:
        now = datetime.utcnow()
        coupons = [c for c in coupons if c.status == CouponStatus.ACTIVE and 
                  c.valid_from <= now and 
                  (c.valid_until is None or c.valid_until >= now)]
    
    return jsonify({
        'coupons': [coupon.to_dict() for coupon in coupons]
    }), 200

@coupon_bp.route('/<int:coupon_id>', methods=['GET'])
def get_coupon(coupon_id):
    """Get a specific coupon by ID"""
    coupon = Coupon.query.get_or_404(coupon_id)
    return jsonify({
        'coupon': coupon.to_dict()
    }), 200

@coupon_bp.route('/', methods=['POST'])
def create_coupon():
    """Create a new coupon for an item"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['item_id', 'code']):
        return jsonify({'error': 'Item ID and coupon code are required'}), 400
    
    # Verify item exists
    item = WishlistItem.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Create new coupon
    new_coupon = Coupon(
        code=data['code'],
        description=data.get('description', ''),
        discount_amount=data.get('discount_amount'),
        is_percentage=data.get('is_percentage', True),
        status=CouponStatus.ACTIVE,
        valid_from=datetime.utcnow(),
        valid_until=data.get('valid_until'),
        item_id=data['item_id']
    )
    
    db.session.add(new_coupon)
    
    # Create notification for the user
    notification = Notification(
        type='coupon',
        message=f"New coupon available for {item.name}: {new_coupon.code}",
        user_id=item.user_id,
        item_id=item.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Coupon created successfully',
        'coupon': new_coupon.to_dict()
    }), 201

@coupon_bp.route('/<int:coupon_id>', methods=['PUT'])
def update_coupon(coupon_id):
    """Update an existing coupon"""
    coupon = Coupon.query.get_or_404(coupon_id)
    data = request.get_json()
    
    # Update coupon fields
    if 'code' in data:
        coupon.code = data['code']
    
    if 'description' in data:
        coupon.description = data['description']
    
    if 'discount_amount' in data:
        coupon.discount_amount = data['discount_amount']
    
    if 'is_percentage' in data:
        coupon.is_percentage = data['is_percentage']
    
    if 'status' in data:
        try:
            coupon.status = CouponStatus(data['status'])
        except ValueError:
            return jsonify({'error': f"Invalid status. Must be one of: {[s.value for s in CouponStatus]}"}), 400
    
    if 'valid_until' in data:
        coupon.valid_until = data['valid_until']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Coupon updated successfully',
        'coupon': coupon.to_dict()
    }), 200

@coupon_bp.route('/<int:coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    """Delete a coupon"""
    coupon = Coupon.query.get_or_404(coupon_id)
    
    db.session.delete(coupon)
    db.session.commit()
    
    return jsonify({
        'message': 'Coupon deleted successfully'
    }), 200

@coupon_bp.route('/simulate/<int:item_id>', methods=['POST'])
def simulate_coupon(item_id):
    """Simulate adding a new coupon for testing purposes"""
    item = WishlistItem.query.get_or_404(item_id)
    data = request.get_json()
    
    # Generate coupon code if not provided
    code = data.get('code', f"SAVE{item.id}{datetime.utcnow().strftime('%m%d')}")
    discount = data.get('discount_amount', 15)
    
    # Create new coupon
    new_coupon = Coupon(
        code=code,
        description=f"Save {discount}% on {item.name}",
        discount_amount=discount,
        is_percentage=True,
        status=CouponStatus.ACTIVE,
        valid_from=datetime.utcnow(),
        valid_until=None,  # No expiration
        item_id=item.id
    )
    
    db.session.add(new_coupon)
    
    # Create notification
    notification = Notification(
        type='coupon',
        message=f"New coupon available for {item.name}: {code}",
        user_id=item.user_id,
        item_id=item.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Coupon simulated successfully',
        'coupon': new_coupon.to_dict()
    }), 201
