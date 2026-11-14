import uuid
from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

# Business rule: every kitten is priced between $800 and $1,000.
# Enforced three ways: form/model validators, a database CHECK constraint,
# and the public filter UI.
MIN_PRICE = 800
MAX_PRICE = 1000
GO_HOME_WEEKS = 12


class Litter(models.Model):
    """A litter groups kittens born on the same date to the same parents.
    Powers the "Meet the parents" section and litter-mate links."""

    name = models.CharField(max_length=100, help_text="Internal label, e.g. 'Duchess x Winston, May 2026'")
    dam_name = models.CharField("Mother", max_length=100)
    sire_name = models.CharField("Father", max_length=100)
    dam_photo = models.ImageField(upload_to="litters/parents/", blank=True, null=True)
    sire_photo = models.ImageField(upload_to="litters/parents/", blank=True, null=True)
    dam_description = models.CharField(max_length=200, blank=True, help_text="e.g. 'Calico longhair, standard Munchkin, 7 lb, TICA registered'")
    sire_description = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-birth_date"]

    def __str__(self):
        return self.name


class Kitten(models.Model):
    class Gender(models.TextChoices):
        UNCONFIRMED = "unconfirmed", "To be confirmed"
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class CoatLength(models.TextChoices):
        SHORTHAIR = "shorthair", "Shorthair"
        LONGHAIR = "longhair", "Longhair"

    class LegLength(models.TextChoices):
        UNCONFIRMED = "unconfirmed", "To be confirmed"
        STANDARD = "standard", "Standard short legs"
        SUPER_SHORT = "super_short", "Super short (rug hugger)"
        NON_STANDARD = "non_standard", "Non-standard (normal legs)"

    class CoatColor(models.TextChoices):
        BLACK = "black", "Black"
        WHITE = "white", "White"
        BLUE = "blue", "Blue (gray)"
        CREAM = "cream", "Cream"
        RED = "red", "Red (orange)"
        CHOCOLATE = "chocolate", "Chocolate"
        LILAC = "lilac", "Lilac"
        SILVER = "silver", "Silver"
        BROWN = "brown", "Brown"
        TRICOLOR = "tricolor", "Tri-color"

    class Pattern(models.TextChoices):
        SOLID = "solid", "Solid"
        TABBY = "tabby", "Tabby"
        CALICO = "calico", "Calico"
        TORTIE = "tortie", "Tortoiseshell"
        BICOLOR = "bicolor", "Bi-color"
        COLORPOINT = "colorpoint", "Colorpoint"
        SMOKE = "smoke", "Smoke"

    class EyeColor(models.TextChoices):
        GOLD = "gold", "Gold"
        GREEN = "green", "Green"
        COPPER = "copper", "Copper"
        BLUE = "blue", "Blue"
        HAZEL = "hazel", "Hazel"
        ODD = "odd", "Odd-eyed"

    class Energy(models.TextChoices):
        UNCONFIRMED = "unconfirmed", "To be confirmed"
        CALM = "calm", "Calm lap cat"
        PLAYFUL = "playful", "Playful"
        ADVENTUROUS = "adventurous", "Adventurous"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        RESERVED = "reserved", "Reserved"
        ADOPTED = "adopted", "Adopted"
        COMING_SOON = "coming_soon", "Coming soon"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    litter = models.ForeignKey(Litter, on_delete=models.SET_NULL, null=True, blank=True, related_name="kittens")

    gender = models.CharField(max_length=12, choices=Gender.choices, default=Gender.UNCONFIRMED)
    coat_length = models.CharField(max_length=12, choices=CoatLength.choices, default=CoatLength.SHORTHAIR)
    leg_length = models.CharField(max_length=14, choices=LegLength.choices, default=LegLength.UNCONFIRMED)
    coat_color = models.CharField(max_length=14, choices=CoatColor.choices)
    pattern = models.CharField(max_length=12, choices=Pattern.choices, default=Pattern.SOLID)
    eye_color = models.CharField(max_length=8, choices=EyeColor.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    available_from = models.DateField(
        null=True, blank=True,
        help_text="Go-home date. Leave blank to use birth date + 12 weeks.",
    )

    price = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(MIN_PRICE), MaxValueValidator(MAX_PRICE)],
        help_text=f"Must be between ${MIN_PRICE} and ${MAX_PRICE:,}.",
    )
    deposit_amount = models.DecimalField(max_digits=6, decimal_places=2, default=200, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AVAILABLE)

    headline = models.CharField(max_length=160, help_text="Short marketing line shown on cards")
    description = models.TextField()
    energy = models.CharField(max_length=12, choices=Energy.choices, default=Energy.UNCONFIRMED)
    personality_tags = models.CharField(
        max_length=160, blank=True,
        help_text="Comma separated, e.g. cuddly, curious, chatty",
    )
    good_with_kids = models.BooleanField(default=True)
    good_with_pets = models.BooleanField(default=True)
    weight_estimate_lb = models.DecimalField(
        "Estimated adult weight (lb)", max_digits=3, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(2), MaxValueValidator(20)],
    )

    vet_checked = models.BooleanField(default=True)
    vaccinations_up_to_date = models.BooleanField(default=True)
    dewormed = models.BooleanField(default=True)
    microchipped = models.BooleanField(default=True)
    litter_trained = models.BooleanField(default=True)
    spay_neuter_agreement = models.BooleanField(default=True, help_text="Sold under a spay/neuter agreement.")
    care_info_confirmed = models.BooleanField(
        default=False,
        help_text="Enable only after the care, health, and household suitability details above are verified.",
    )
    registry = models.CharField(max_length=60, blank=True, help_text="e.g. 'TICA registered'")
    health_guarantee_years = models.PositiveSmallIntegerField(default=1)

    cover_photo = models.ImageField(upload_to="kittens/covers/")
    cover_alt = models.CharField(max_length=160, blank=True, help_text="Optional custom alt text for the cover photo.")
    video_url = models.URLField(blank=True, help_text="Optional YouTube or Vimeo link.")

    nationwide_delivery_available = models.BooleanField(default=True)
    delivery_notes = models.CharField(
        max_length=255, blank=True,
        default="Pickup by appointment, or ground / flight-nanny delivery across the continental US.",
    )

    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["gender", "coat_length", "coat_color"]),
            models.Index(fields=["price"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=MIN_PRICE) & Q(price__lte=MAX_PRICE),
                name="kitten_price_between_800_and_1000",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    # ----- slug / URLs -------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.name}-{self.coat_color}-{self.pattern}-munchkin-kitten")[:90]
            slug, n = base, 1
            while Kitten.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("kittens:detail", kwargs={"slug": self.slug})

    # ----- derived display values -------------------------------------
    @property
    def look(self):
        """Human colour description, e.g. 'Calico', 'Black', 'Red Tabby'."""
        if self.pattern == self.Pattern.CALICO:
            return "Calico"
        if self.pattern == self.Pattern.SOLID:
            return self.get_coat_color_display().split(" (")[0]
        return f"{self.get_coat_color_display().split(' (')[0]} {self.get_pattern_display()}"

    @property
    def listing_title(self):
        return f"{self.look} {self.get_coat_length_display()} Munchkin Kitten"

    @property
    def age_weeks(self):
        if not self.date_of_birth:
            return None
        return max(0, (timezone.localdate() - self.date_of_birth).days // 7)

    @property
    def go_home_date(self):
        if self.available_from:
            return self.available_from
        if self.date_of_birth:
            return self.date_of_birth + timedelta(weeks=GO_HOME_WEEKS)
        return None

    @property
    def weeks_until_ready(self):
        if not self.go_home_date:
            return None
        days = (self.go_home_date - timezone.localdate()).days
        return max(0, -(-days // 7))

    @property
    def is_ready(self):
        return bool(self.go_home_date and self.go_home_date <= timezone.localdate())

    @property
    def readiness_label(self):
        if self.status == self.Status.ADOPTED:
            return "Adopted"
        if not self.go_home_date:
            return "Go-home timing to be confirmed"
        if self.is_ready:
            return "Ready for a new home"
        weeks = self.weeks_until_ready
        return f"Ready in {weeks} week{'s' if weeks != 1 else ''}"

    @property
    def age_label(self):
        return f"{self.age_weeks} weeks" if self.age_weeks is not None else "Age to be confirmed"

    @property
    def personality_list(self):
        return [t.strip() for t in self.personality_tags.split(",") if t.strip()]

    @property
    def is_open(self):
        return self.status in (self.Status.AVAILABLE, self.Status.COMING_SOON)

    @property
    def alt_text(self):
        return self.cover_alt or f"{self.name}, a {self.look.lower()} {self.get_coat_length_display().lower()} Munchkin kitten"

    @property
    def sitemap_images(self):
        images = []
        if self.cover_photo:
            images.append((self.cover_photo.url, self.alt_text))
        return images


class KittenImage(models.Model):
    """Gallery photos for a kitten (cover photo plus as many angles as you like)."""

    kitten = models.ForeignKey(Kitten, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="kittens/gallery/")
    caption = models.CharField(max_length=120, blank=True)
    ordering = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "id"]

    def __str__(self):
        return f"Photo for {self.kitten.name} ({self.ordering})"

    @property
    def alt_text(self):
        return self.caption or f"{self.kitten.name}, Munchkin kitten"
