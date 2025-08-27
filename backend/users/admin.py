from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Additional", {
            'fields': ('bio', 'avatar_url', 'is_email_verified')  # removed 'role'
        }),
    )
    list_display = ('id', 'username', 'is_email_verified', 'is_staff')  # removed 'role'
