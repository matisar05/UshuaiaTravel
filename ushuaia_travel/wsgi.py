import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ushuaia_travel.settings")

application = get_wsgi_application()

try:
    from ushuaia_travel.shutdown import register_shutdown_handlers
    register_shutdown_handlers()
except (ValueError, ImportError):
    pass
