from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration - Load from environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-productivity-tracker-2026')
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Fix PostgreSQL URL scheme for SQLAlchemy 1.4+
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    # Use instance directory for SQLite by default (consistent local path)
    os.makedirs(app.instance_path, exist_ok=True)
    default_sqlite_path = os.path.join(app.instance_path, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or f"sqlite:///{default_sqlite_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Environment-based settings
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # CSRF Configuration - Enable in production
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Session Configuration
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.permanent_session_lifetime = 3600

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.routes import main
    app.register_blueprint(main)

    return app
