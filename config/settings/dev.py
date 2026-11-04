"""The Sunwai — Development Settings"""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# In-memory channel layer for dev
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Console email for dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar (if installed)
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
