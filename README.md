# WishTracker - Wish List App

A comprehensive wish list application that allows users to categorize items, track prices, and receive notifications for price drops and available coupons.

## Features

- **User Authentication**: Register, login, and manage multiple user accounts
- **Item Categorization**: Organize wish list items by categories
- **Price Tracking**: Monitor price changes over time with historical data
- **Price Drop Alerts**: Get notified when prices drop on your wish list items
- **Coupon Detection**: Track and be alerted about available coupons for your items
- **Notification System**: Visual indicators for price drops and coupon availability
- **Simple, Fun UI**: Clean interface with pastel colors

## Project Structure

```
wishlist_app/
├── src/
│   ├── models/
│   │   └── models.py       # Database models for users, items, prices, coupons, etc.
│   ├── routes/
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── category.py     # Category management endpoints
│   │   ├── coupon.py       # Coupon management endpoints
│   │   ├── notification.py # Notification endpoints
│   │   ├── price.py        # Price tracking endpoints
│   │   ├── user.py         # User management endpoints
│   │   └── wishlist.py     # Wish list item endpoints
│   ├── static/
│   │   └── index.html      # Landing page
│   └── main.py             # Main application entry point
├── tests.py                # Automated tests for all endpoints
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user
- `POST /api/auth/logout` - Logout a user

### Users
- `GET /api/users/` - Get all users
- `GET /api/users/<user_id>` - Get a specific user
- `PUT /api/users/<user_id>` - Update a user
- `DELETE /api/users/<user_id>` - Delete a user

### Categories
- `GET /api/categories/` - Get all categories
- `GET /api/categories/<category_id>` - Get a specific category
- `POST /api/categories/` - Create a new category
- `PUT /api/categories/<category_id>` - Update a category
- `DELETE /api/categories/<category_id>` - Delete a category

### Wish List Items
- `GET /api/wishlist/?user_id=<user_id>` - Get all items for a user
- `GET /api/wishlist/<item_id>` - Get a specific item
- `POST /api/wishlist/` - Create a new item
- `PUT /api/wishlist/<item_id>` - Update an item
- `DELETE /api/wishlist/<item_id>` - Delete an item
- `GET /api/wishlist/price-drops?user_id=<user_id>` - Get items with price drops

### Price Tracking
- `POST /api/prices/update/<item_id>` - Update price for an item
- `GET /api/prices/history/<item_id>` - Get price history for an item
- `GET /api/prices/drops?user_id=<user_id>` - Get items with price drops
- `POST /api/prices/simulate-drop/<item_id>` - Simulate a price drop (for testing)

### Coupons
- `GET /api/coupons/?item_id=<item_id>` - Get coupons for an item
- `GET /api/coupons/?user_id=<user_id>` - Get coupons for all items of a user
- `GET /api/coupons/<coupon_id>` - Get a specific coupon
- `POST /api/coupons/` - Create a new coupon
- `PUT /api/coupons/<coupon_id>` - Update a coupon
- `DELETE /api/coupons/<coupon_id>` - Delete a coupon
- `POST /api/coupons/simulate/<item_id>` - Simulate adding a coupon (for testing)

### Notifications
- `GET /api/notifications/?user_id=<user_id>` - Get notifications for a user
- `PUT /api/notifications/<notification_id>/read` - Mark a notification as read
- `PUT /api/notifications/read-all?user_id=<user_id>` - Mark all notifications as read
- `DELETE /api/notifications/<notification_id>` - Delete a notification

## Installation and Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the database:
   - The application is configured to use MySQL by default
   - Database connection settings can be modified in `src/main.py`

4. Run the application:
   ```
   python src/main.py
   ```
   
5. Access the application at `http://localhost:5000`

## Testing

Run the automated tests to verify all functionality:

```
python tests.py
```

## Frontend Development

The current implementation includes a landing page and backend API. To develop the full frontend:

1. Use the existing API endpoints to build UI components
2. Follow the pastel color scheme as specified in the landing page
3. Implement visual indicators for price drops and coupon notifications
4. Create responsive designs for both desktop and mobile views

## License

This project is licensed under the MIT License.
