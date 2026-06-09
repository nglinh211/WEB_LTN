from django.contrib import admin

from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("full_name", "user__username", "user__email", "phone")
