"""
Production settings for deployment
Import this in your deployment platform's environment
"""
import os
import dj_database_url
from pathlib import Path
from .settings import *

# Override for production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Database - Use environment variable (PostgreSQL for most platforms)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files with WhiteNoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Media files - Use cloud storage in production (AWS S3, Cloudinary, etc.)
# For now, using local storage (not recommended for production)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

