"""Settings package — defaults to dev."""
import os
from decouple import config

env = config('DJANGO_SETTINGS_MODULE', default='config.settings.dev')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', env)
