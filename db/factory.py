# db/factory.py
import mysql.connector
from flask import current_app, g
import sqlite3



def initialize_db():
    try:
        db_type = current_app.config.get('DB_TYPE', 'sqlite')  # Default to sqlite if not specified

        if db_type == 'mysql':
            connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            current_app.logger.info("Successfully connected to MySQL database.")
        
        elif db_type == 'sqlite':
            connection = sqlite3.connect(current_app.config['DATABASE'])
            current_app.logger.info("Successfully connected to SQLite database.")
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        return connection

    except mysql.connector.Error as err:
        current_app.logger.error(f"Database connection failed: {err}")
        raise
    except sqlite3.Error as err:
        current_app.logger.error(f"SQLite connection failed: {err}")
        raise
    except Exception as e:
        current_app.logger.error(f"Error creating database: {e}")
        raise



# Factory class to get the database - What is this for? 
class DatabaseFactory:
    @staticmethod
    def get_database():
        connection = initialize_db()
        db_type = current_app.config.get('DB_TYPE', 'sqlite')
        
        if db_type == 'sqlite':
            return SQLiteDatabase(connection)
        elif db_type == 'mysql':
            return MySQLDatabase(connection)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
    @staticmethod
    def close_db(e=None):
        if 'db' in g:
            g.db.close()
            g.pop('db', None)

class Database:
    def __init__(self, connection):
        self.connection = connection

    def get_connection(self):
        raise NotImplementedError("Subclasses must implement get_connection()")
    
    def close_connection(self, connection):
        raise NotImplementedError("Subclasses must implement close_connection()")

class MySQLDatabase(Database):
    def get_connection(self):
        return self.connection
    
    def close_connection(self, connection):
        if connection is not None:
            try:
                connection.close()
                current_app.logger.info("MySQL connection closed successfully.")
            except mysql.connector.Error as err:
                current_app.logger.error(f"Error closing MySQL connection: {err}")

class SQLiteDatabase(Database):
    def get_connection(self):
        return self.connection
    
    def close_connection(self, connection):
        if connection is not None:
            try:
                connection.close()
                current_app.logger.info("SQLite connection closed successfully.")
            except sqlite3.Error as err:
                current_app.logger.error(f"Error closing SQLite connection: {err}")
