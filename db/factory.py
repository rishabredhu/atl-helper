# db/factory.py
from flask import g
import mysql.connector
import os

class DatabaseFactory:
    @staticmethod
    def get_db():
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'atluser'),
                password=os.getenv('MYSQL_PASSWORD', 'atlpass'),
                database=os.getenv('MYSQL_DATABASE', 'atl')
            )
        return g.db

def init_app(app):
    """Initialize the database with the Flask app"""
    @app.before_request
    def init_database():
        if not hasattr(g, 'db_initialized'):
            g.db_initialized = True

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

def get_db():
    return DatabaseFactory.get_db()