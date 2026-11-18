"""ASGI config for American Munchkin House (same boot fallback as wsgi.py)."""

import os

from django.core.asgi import get_asgi_application
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if os.environ.get("RUN_MAIN") != "true" and os.environ.get("AUTO_MIGRATE", "True").lower() in ("1", "true", "yes"):
    try:
        call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
    except Exception:  # pragma: no cover
        pass

application = get_asgi_application()
