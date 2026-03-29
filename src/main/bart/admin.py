from django.contrib import admin
from .models import BARTQuery


@admin.register(BARTQuery)
class BARTQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at")
    readonly_fields = ("response", "created_at")
    search_fields = ("prompt", "response")
