"""
Database initialization middleware for serverless/Vercel deployments.
Ensures /tmp/db.sqlite3 is initialized with tables and seeded data on first request.
"""
import os
import shutil
import logging
from pathlib import Path
from django.db import connection

logger = logging.getLogger(__name__)

_initialized = False


class EnsureDatabaseMiddleware:
    """Ensures database tables exist on serverless deployments."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _initialized
        if not _initialized:
            self._ensure_db()
            _initialized = True
        return self.get_response(request)

    @staticmethod
    def _ensure_db():
        try:
            tables = connection.introspection.table_names()
            if 'accounts_user' in tables:
                return

            base_dir = Path(__file__).resolve().parent.parent
            seed_file = base_dir / 'seed_db.sqlite3'
            db_file = Path('/tmp/db.sqlite3')

            # If seed_db.sqlite3 is bundled, copy it over /tmp/db.sqlite3
            if seed_file.exists() and seed_file.stat().st_size > 1000:
                try:
                    connection.close()
                    shutil.copyfile(seed_file, db_file)
                    # Re-check after copy
                    if 'accounts_user' in connection.introspection.table_names():
                        logger.info("Successfully copied seed_db.sqlite3 to /tmp/db.sqlite3")
                        return
                except Exception as e:
                    logger.warning(f"Copying seed_db.sqlite3 failed: {e}")

            # Fallback: run migrate and seed_sunwai commands
            logger.info("Running migrate and seed_sunwai...")
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            call_command('seed_sunwai')
            logger.info("Database migration and seed complete.")
        except Exception as e:
            logger.error(f"Error in EnsureDatabaseMiddleware: {e}", exc_info=True)
