from django.core.management.base import BaseCommand

from core.journal_seed import ARTICLES
from core.models import Post


class Command(BaseCommand):
    help = "Publishes the starter journal articles (idempotent: existing titles are skipped)."

    def handle(self, *args, **options):
        created = 0
        for art in ARTICLES:
            _, was_created = Post.objects.get_or_create(
                title=art["title"],
                defaults={k: art[k] for k in ("category", "excerpt", "meta_description", "content")},
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Published {created} journal articles ({len(ARTICLES) - created} already existed)."))
