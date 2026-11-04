"""The Sunwai — Development & Serverless Settings"""
import os
from pathlib import Path
from .base import *  # noqa: F401,F403
from decouple import config
import dj_database_url

DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

# Database: use DATABASE_URL if available, else SQLite
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    db_file = Path('/tmp/db.sqlite3') if os.environ.get('VERCEL') else (BASE_DIR / 'db.sqlite3')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_file,
        }
    }

# In-memory channel layer for dev / serverless
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Console email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
