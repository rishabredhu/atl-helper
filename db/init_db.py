# db/init_db.py
from db.factory import DatabaseFactory

def main():
    print("Starting database initialization...")
    try:
        DatabaseFactory.init_db()
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        exit(1)

if __name__ == "__main__":
    main()