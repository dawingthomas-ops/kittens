from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["path", "kitten", "created_at"]
    list_filter = ["created_at"]
