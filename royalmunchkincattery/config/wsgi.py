"""
WSGI config for Royal Munchkin Cattery.

Mirrors the findapomsky setup: on platforms where the release step can be
skipped (e.g. a recreated Render free instance with SQLite) the schema is
created on first boot. Set AUTO_MIGRATE=False to disable.
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if os.environ.get("RUN_MAIN") != "true" and os.environ.get("AUTO_MIGRATE", "True").lower() in ("1", "true", "yes"):
    try:
        call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
    except Exception:  # pragma: no cover - never block boot on a migration hiccup
        pass

application = get_wsgi_application()
