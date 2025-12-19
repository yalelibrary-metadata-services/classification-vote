import os
from datetime import timedelta

class Config:
    """Flask application configuration"""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'classification.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False},
        'pool_pre_ping': True,
    }

    # Session
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Admin settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'changeme'

    # Default classification settings
    DEFAULT_CONTENTIOUS_THRESHOLD = 0.70  # 70% agreement required
    MIN_VOTES_FOR_CONTENTIOUS = 3  # Minimum votes before marking contentious

    # XML export settings
    DEFAULT_EXPORT_CONFIDENCE = 0.60  # Only export notes with 60%+ confidence

    # Upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload size
    ALLOWED_EXTENSIONS = {'xml'}
