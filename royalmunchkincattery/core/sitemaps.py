from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from kittens.models import Kitten

from .landing_pages import LANDING_PAGES
from .models import Post


class KittenSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Kitten.objects.exclude(status=Kitten.Status.ADOPTED)

    def lastmod(self, obj):
        return obj.updated_at


class LandingPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return list(LANDING_PAGES.keys()) + ["__guide__"]

    def location(self, item):
        if item == "__guide__":
            return reverse("core:breed_guide")
        return reverse("core:landing", kwargs={"slug": item})


class JournalSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return [
            "core:home", "kittens:list", "kittens:match", "core:about", "core:faq", "core:delivery",
            "core:contact", "core:waitlist", "core:journal_list", "reviews:list", "core:privacy", "core:terms",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {"core:home": 1.0, "kittens:list": 0.95}.get(item, 0.6)
