"""
WSGI config for The Sunwai project.
"""
import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# On Vercel serverless, ensure SQLite database in /tmp is populated
if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
    db_dest = Path('/tmp/db.sqlite3')
    base_dir = Path(__file__).resolve().parent.parent
    seed_src = base_dir / 'seed_db.sqlite3'
    
    # 1. Try copying pre-seeded database if present
    if not db_dest.exists() or db_dest.stat().st_size == 0:
        if seed_src.exists():
            try:
                shutil.copyfile(seed_src, db_dest)
            except Exception as e:
                print(f"Notice: copying seed_db.sqlite3 failed: {e}")

    # 2. Verify tables exist; if missing, auto-migrate and seed
    try:
        import django
        django.setup()
        from django.db import connection
        tables = connection.introspection.table_names()
        if 'accounts_user' not in tables:
            from django.core.management import call_command
            print("Vercel notice: accounts_user missing, running migrate and seed_sunwai...")
            call_command('migrate', interactive=False)
            call_command('seed_sunwai')
    except Exception as e:
        print(f"Notice during Vercel DB initialization: {e}")

application = get_wsgi_application()
app = application
