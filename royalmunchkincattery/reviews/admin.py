from django.contrib import admin
from django.utils import timezone

from .models import Testimonial


@admin.action(description="Approve selected testimonials")
def approve_testimonials(modeladmin, request, queryset):
    queryset.update(is_approved=True, approved_at=timezone.now(), approved_by=request.user)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["author_name", "kitten", "rating", "is_approved", "submitted_at"]
    list_filter = ["is_approved", "rating"]
    search_fields = ["author_name", "body", "kitten__name"]
    actions = [approve_testimonials]
    readonly_fields = [
        "id", "submitted_at", "approved_at", "approved_by", "author_name",
        "author_city_state", "rating", "photo", "kitten", "reservation", "body",
    ]
    fieldsets = (
        ("Customer", {"fields": ("author_name", "author_city_state", "rating", "photo")}),
        ("Linked record", {"fields": ("kitten", "reservation")}),
        ("Review", {"fields": ("body", "is_approved")}),
        ("Moderation", {"fields": ("approved_at", "approved_by", "submitted_at", "id")}),
    )

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        previous = (
            Testimonial.objects.filter(pk=obj.pk).values("is_approved").first()
            if change else None
        )
        if obj.is_approved:
            if not previous or not previous["is_approved"] or not obj.approved_at:
                obj.approved_at = timezone.now()
                obj.approved_by = request.user
        else:
            obj.approved_at = None
            obj.approved_by = None
        super().save_model(request, obj, form, change)
