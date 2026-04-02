"""
This file updates the Flask app configuration for production/Cloudflare deployment.
Import this in app.py to load production settings.
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration for Flask app"""
    
    # Security
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CORS/Security Headers (for Cloudflare)
    PREFERRED_URL_SCHEME = "https"
    
    # Debug
    DEBUG = False
    TESTING = False
    
    # App
    JSON_SORT_KEYS = False


class DevelopmentConfig:
    """Development configuration"""
    SECRET_KEY = "dev-key-remember-to-change"
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class TestingConfig:
    """Testing configuration"""
    TESTING = True
    SECRET_KEY = "test-key"
    WTF_CSRF_ENABLED = False


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()
