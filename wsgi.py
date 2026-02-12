"""
WSGI entry point for production servers (Gunicorn, Waitress, etc.)
"""
from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
