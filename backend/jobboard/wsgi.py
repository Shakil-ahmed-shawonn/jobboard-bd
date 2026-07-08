"""WSGI entrypoint for JobBoard BD — used by Gunicorn on Render."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobboard.settings")
application = get_wsgi_application()
