from django.contrib import admin

from .models import ContactMessage, Post, SiteSettings, WaitlistEntry


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_published", "published_at"]
    list_filter = ["is_published", "category", "published_at"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Content", {"fields": ("title", "slug", "category", "excerpt", "content")}),
        ("SEO", {"fields": ("meta_description",)}),
        ("Media", {"fields": ("featured_image",)}),
        ("Status", {"fields": ("is_published", "published_at")}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "is_handled", "created_at"]
    list_filter = ["is_handled", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["ip_address", "created_at"]


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "preferred_gender", "preferred_coat_length", "preferred_colors", "is_contacted", "created_at"]
    list_filter = ["is_contacted", "preferred_gender", "preferred_coat_length"]
    search_fields = ["name", "email", "preferred_colors"]
    readonly_fields = ["ip_address", "created_at"]
