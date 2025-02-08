# db/factory.py
import mysql.connector
from mysql.connector import Error
import time
import os
from flask import g

class DatabaseFactory:
    @staticmethod
    def wait_for_db(max_retries=30, delay=1):
        """Wait for database to become available"""
        retries = 0
        while retries < max_retries:
            try:
                conn = mysql.connector.connect(
                    host=os.getenv('MYSQL_HOST', 'db'),
                    user=os.getenv('MYSQL_USER', 'atluser'),
                    password=os.getenv('MYSQL_PASSWORD', 'atlpass'),
                    database=os.getenv('MYSQL_DATABASE', 'atl')
                )
                conn.close()
                print("Database is available!")
                return True
            except Error as e:
                print(f"Database unavailable, waiting... (Attempt {retries + 1}/{max_retries})")
                retries += 1
                time.sleep(delay)
        return False

    @staticmethod
    def init_db():
        """Initialize the database with schema and initial data"""
        if not DatabaseFactory.wait_for_db():
            raise Exception("Database connection timeout")

        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'db'),
            user=os.getenv('MYSQL_USER', 'atluser'),
            password=os.getenv('MYSQL_PASSWORD', 'atlpass'),
            database=os.getenv('MYSQL_DATABASE', 'atl')
        )
        cursor = conn.cursor()

        try:
            # Execute schema creation
            with open('db/schema.sql', 'r') as f:
                schema_sql = f.read()
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
            
            # Execute initial data insertion
            with open('db/data.sql', 'r') as f:
                data_sql = f.read()
                for statement in data_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
            
            conn.commit()
            print("Database initialized successfully!")
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_db():
        """Get database connection"""
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'db'),
                user=os.getenv('MYSQL_USER', 'atluser'),
                password=os.getenv('MYSQL_PASSWORD', 'atlpass'),
                database=os.getenv('MYSQL_DATABASE', 'atl')
            )
        return g.db

def init_app(app):
    """Initialize the database with the Flask app"""
    @app.before_first_request
    def init_database():
        DatabaseFactory.wait_for_db()

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

# Create an instance of the database factory
def get_db():
    return DatabaseFactory.get_db()