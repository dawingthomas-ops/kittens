from django.contrib import admin
from django.utils.html import format_html

from .models import Kitten, KittenImage, Litter


class KittenImageInline(admin.TabularInline):
    model = KittenImage
    extra = 2
    max_num = 10


@admin.register(Kitten)
class KittenAdmin(admin.ModelAdmin):
    list_display = ["thumb", "name", "gender", "coat_length", "look_display", "status", "price", "is_featured", "view_count", "created_at"]
    list_display_links = ["thumb", "name"]
    list_filter = ["status", "gender", "coat_length", "leg_length", "coat_color", "pattern", "energy", "is_featured"]
    list_editable = ["status", "price", "is_featured"]
    search_fields = ["name", "headline", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [KittenImageInline]
    readonly_fields = ["id", "view_count", "created_at", "updated_at"]
    fieldsets = (
        ("Identity", {"fields": ("id", "name", "slug", "litter", "gender", "date_of_birth", "available_from")}),
        ("Appearance", {"fields": ("coat_length", "leg_length", "coat_color", "pattern", "eye_color", "weight_estimate_lb", "cover_photo", "cover_alt", "video_url")}),
        ("Listing", {"fields": ("status", "price", "deposit_amount", "headline", "description", "is_featured")}),
        ("Personality", {"fields": ("energy", "personality_tags", "good_with_kids", "good_with_pets")}),
        ("Health", {"fields": ("vet_checked", "vaccinations_up_to_date", "dewormed", "microchipped", "litter_trained", "spay_neuter_agreement", "care_info_confirmed", "registry", "health_guarantee_years")}),
        ("Delivery", {"fields": ("nationwide_delivery_available", "delivery_notes")}),
        ("Meta", {"fields": ("view_count", "created_at", "updated_at")}),
    )

    @admin.display(description="Photo")
    def thumb(self, obj):
        if obj.cover_photo:
            return format_html('<img src="{}" style="width:44px;height:44px;object-fit:cover;border-radius:50%">', obj.cover_photo.url)
        return "-"

    @admin.display(description="Look")
    def look_display(self, obj):
        return obj.look


@admin.register(Litter)
class LitterAdmin(admin.ModelAdmin):
    list_display = ["name", "dam_name", "sire_name", "birth_date"]
