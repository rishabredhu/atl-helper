# app/__init__.py
from flask import Flask
from db.factory import init_app
from .routes.main import main_bp
from .routes.customers import customers_bp
from .routes.bookings import bookings_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Initialize database connection handling
    init_app(app)
         
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(bookings_bp)
    
    return app