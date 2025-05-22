import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from src.models.models import db, User, Category, WishlistItem, PriceHistory, Coupon, Notification
from src.routes.user import user_bp
from src.routes.wishlist import wishlist_bp
from src.routes.category import category_bp
from src.routes.auth import auth_bp
from src.routes.price import price_bp
from src.routes.coupon import coupon_bp
from src.routes.notification import notification_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
app.register_blueprint(category_bp, url_prefix='/api/categories')
app.register_blueprint(price_bp, url_prefix='/api/prices')
app.register_blueprint(coupon_bp, url_prefix='/api/coupons')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add default categories if they don't exist
    default_categories = [
        "Electronics", "Clothing", "Books", "Home & Kitchen", 
        "Beauty", "Toys & Games", "Sports & Outdoors", "Other"
    ]
    
    existing_categories = Category.query.all()
    existing_names = [c.name for c in existing_categories]
    
    for category_name in default_categories:
        if category_name not in existing_names:
            new_category = Category(name=category_name)
            db.session.add(new_category)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
