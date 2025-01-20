"""
WSGI config for urlshortener project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from .settings import BASE_DIR

STATIC_URL = "/static/"

# The directory where static files will be collected
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Optionally, add the directories where static files are stored
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urlshortener.settings")

application = get_wsgi_application()

from whitenoise import WhiteNoise

application = WhiteNoise(
    application, root=os.path.join(os.path.dirname(__file__), "staticfiles")
)
