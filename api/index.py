"""Vercel serverless entrypoint."""
from config.wsgi import app

# Expose app for Vercel
application = app
