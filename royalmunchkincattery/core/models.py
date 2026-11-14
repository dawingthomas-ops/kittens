import re
import uuid

from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

SETTINGS_CACHE_KEY = "core:site_settings:v1"


class Post(models.Model):
    """Journal articles: care guides, litter news and breed education.
    Content is trusted admin-authored HTML."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True, help_text="Shown on cards and used as the meta description if none is set.")
    meta_description = models.CharField(max_length=160, blank=True, help_text="Optional. 150-160 characters ranks best.")
    content = models.TextField(help_text="HTML allowed (h2, h3, p, ul, ol, a, strong).")
    featured_image = models.ImageField(upload_to="posts/", null=True, blank=True)
    category = models.CharField(max_length=60, blank=True, default="Care guide")
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "post"
            slug, n = base, 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:journal_detail", kwargs={"slug": self.slug})

    @property
    def plain_text(self):
        return re.sub(r"\s+", " ", strip_tags(self.content)).strip()

    @property
    def reading_time(self):
        words = len(self.plain_text.split())
        return max(1, round(words / 220))

    @property
    def seo_description(self):
        return self.meta_description or self.excerpt or self.plain_text[:155]


class SiteSettings(models.Model):
    """Singleton row holding editable business info so the phone number,
    location and social links can change without a code deploy."""

    business_name = models.CharField(max_length=120, default="Royal Munchkin Cattery")
    tagline = models.CharField(max_length=200, default="Home-raised Munchkin kittens with royal manners")
    city = models.CharField(max_length=100, default="Dallas", help_text="Used in schema.org markup. Clear it to hide the address.")
    state = models.CharField(max_length=2, default="TX", blank=True)
    contact_phone = models.CharField(max_length=24, blank=True, help_text="Digits with country code, e.g. +15551234567")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Digits only, e.g. 15551234567")
    contact_email = models.EmailField(default="dawingthomas@gmail.com")
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    kittens_placed_count = models.PositiveIntegerField(
        default=0, help_text="Shown on the homepage only when above zero. Use a real number."
    )
    announcement = models.CharField(max_length=160, blank=True, help_text="Optional banner above the header (e.g. 'New litter due in March').")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(SETTINGS_CACHE_KEY)

    def delete(self, *args, **kwargs):
        cache.delete(SETTINGS_CACHE_KEY)
        return super().delete(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cache.get(SETTINGS_CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(SETTINGS_CACHE_KEY, obj, 300)
        return obj

    @property
    def same_as(self):
        return [u for u in (self.instagram_url, self.facebook_url, self.tiktok_url, self.youtube_url) if u]


class ContactMessage(models.Model):
    """Messages from the contact form. Persisted before emailing, so a lead
    is never lost if SMTP is down."""

    submission_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=24, blank=True)
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField(max_length=2000)
    is_handled = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.subject or 'Contact message'}"


class WaitlistEntry(models.Model):
    """Interest in an upcoming litter, with the buyer's preferences so the
    right families hear first."""

    class Gender(models.TextChoices):
        ANY = "any", "No preference"
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class CoatLength(models.TextChoices):
        ANY = "any", "No preference"
        SHORT = "shorthair", "Shorthair"
        LONG = "longhair", "Longhair"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=24, blank=True)
    preferred_gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.ANY)
    preferred_coat_length = models.CharField(max_length=12, choices=CoatLength.choices, default=CoatLength.ANY)
    preferred_colors = models.CharField(max_length=160, blank=True, help_text="e.g. calico, black, red tabby")
    notes = models.TextField(max_length=1000, blank=True)
    is_contacted = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Waitlist entries"

    def __str__(self):
        return f"{self.name} <{self.email}>"
