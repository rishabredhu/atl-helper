# connect.py
from db.factory import get_db

def execute_sql_file(cursor, file_path):
    """
    Reads an SQL file and executes each statement.
    Note: This simple split on semicolons may not work for all SQL files,
    especially those with complex syntax. For more robust splitting, consider
    using a dedicated SQL parser like 'sqlparse'.
    """
    with open(file_path, 'r') as f:
        sql_content = f.read()

    # Split the file content by semicolon
    statements = sql_content.split(';')
    for statement in statements:
        # Strip whitespace and ignore empty statements
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Error executing statement:\n{statement}\nError: {e}")

def database_exists(cursor, db_name):
    """
    Check if a database with the given name exists
    """
    try:
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking database existence: {e}")
        return False

def init_db():
    """
    Initialize the database by executing the schema and data SQL files.
    Only initializes if the database doesn't already exist.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if database already exists
    if database_exists(cursor, 'atl'):
        print("Database 'atl' already exists. Re-building DB...")
        # Drop existing database
        cursor.execute("DROP DATABASE atl")
        conn.commit()
        print("Existing database dropped.")
        # Create fresh database
        cursor.execute("CREATE DATABASE atl") 
        conn.commit()
        cursor.execute("USE atl")
        print("Created new database 'atl'.")

    # Execute schema creation SQL (schema.sql)
    try:
        execute_sql_file(cursor, 'db/atl-local.sql')
        print("Schema created successfully.")
    except Exception as e:
        print("Error executing atl-local.sql:", e)
        conn.rollback()
        return

    # Execute data insertion SQL (choose the appropriate file for your environment)
    try:
        execute_sql_file(cursor, 'db/atl-local.sql')
    except Exception as e:
        print("Error executing atl-local.sql:", e)
        conn.rollback()
        return

    # Commit the changes and clean up
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
