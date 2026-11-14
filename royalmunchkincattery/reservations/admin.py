from django.contrib import admin
from django.utils.html import format_html

from .models import Reservation


@admin.action(description="Mark selected as contacted")
def mark_contacted(modeladmin, request, queryset):
    queryset.filter(status=Reservation.Status.NEW).update(status=Reservation.Status.CONTACTED)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email_link", "kitten", "contact_preference", "message_channel", "delivery_method", "status", "shipping_state", "created_at"]
    list_filter = ["status", "contact_preference", "message_channel", "delivery_method", "shipping_state"]
    search_fields = ["full_name", "email", "phone", "kitten__name"]
    readonly_fields = ["id", "ip_address", "created_at", "updated_at"]
    actions = [mark_contacted]
    fieldsets = (
        ("Customer", {"fields": ("full_name", "email", "phone", "contact_preference", "message_channel")}),
        ("Kitten", {"fields": ("kitten", "status")}),
        ("Delivery", {"fields": ("shipping_city", "shipping_state", "delivery_method", "has_other_pets")}),
        ("Message", {"fields": ("message", "admin_notes")}),
        ("System", {"fields": ("id", "ip_address", "created_at", "updated_at")}),
    )

    @admin.display(description="Email")
    def email_link(self, obj):
        # format_html escapes the address, so it is safe even if hostile.
        return format_html('<a href="mailto:{0}">{0}</a>', obj.email)
