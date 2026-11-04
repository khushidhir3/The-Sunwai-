"""Vercel serverless entrypoint."""
import os
from pathlib import Path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

# Auto-migrate and seed in /tmp for serverless if using SQLite
if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    db_path = Path('/tmp/db.sqlite3')
    if not db_path.exists():
        try:
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            call_command('seed_sunwai')
        except Exception as e:
            print(f'Vercel SQLite init notice: {e}')

from config.wsgi import app

application = app
