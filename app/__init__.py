# app/__init__.py
from flask import Flask # see next section
from flask import g
import os
import mysql.connector
from flask import current_app
from db.factory import DatabaseFactory


def create_app():
    app = Flask(__name__)

    # Determine the environment and load the appropriate config
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Register the database teardown function so connections are closed automatically
    close_db = DatabaseFactory.get_database().close_connection
    app.teardown_appcontext(close_db)

    # Import and register the blueprint from your routes
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    print(app.url_map)  # This will show all registered routes after registering the blueprint

    return app
