from flask import Blueprint, request, jsonify
from src.models.models import db, Category

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['GET'])
def get_all_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category by ID"""
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'category': category.to_dict()
    }), 200

@category_bp.route('/', methods=['POST'])
def create_category():
    """Create a new category"""
    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({'error': 'Category name is required'}), 400
    
    # Check if category already exists
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 409
    
    # Create new category
    new_category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': new_category.to_dict()
    }), 201

@category_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing category"""
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    # Update category fields
    if 'name' in data:
        # Check if the new name already exists for another category
        existing = Category.query.filter_by(name=data['name']).first()
        if existing and existing.id != category_id:
            return jsonify({'error': 'Category name already exists'}), 409
        category.name = data['name']
    
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has items
    if category.items:
        return jsonify({
            'error': 'Cannot delete category with associated items. Reassign items first.'
        }), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category deleted successfully'
    }), 200
