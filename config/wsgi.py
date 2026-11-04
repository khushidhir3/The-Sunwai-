"""
WSGI config for The Sunwai project.
"""
import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# On Vercel serverless, copy pre-seeded database to writable /tmp directory
if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    db_dest = Path('/tmp/db.sqlite3')
    seed_src = Path(__file__).resolve().parent.parent / 'seed_db.sqlite3'
    if not db_dest.exists() or db_dest.stat().st_size == 0:
        if seed_src.exists():
            try:
                shutil.copyfile(seed_src, db_dest)
            except Exception as e:
                print(f"Error copying seed_db.sqlite3 to /tmp: {e}")

application = get_wsgi_application()
app = application

