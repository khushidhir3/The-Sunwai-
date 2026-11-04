"""Vercel serverless entrypoint."""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

from config.wsgi import app

application = app
