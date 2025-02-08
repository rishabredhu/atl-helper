# run.py
from app import create_app
from db.factory import DatabaseFactory
app = create_app()

if __name__ == '__main__':
    # Wait for database before starting
    # DatabaseFactory.wait_for_db()
    app.run(port=5001, debug=True)
