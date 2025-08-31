from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StatusUpdate, UserProfile


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'profile_picture', 'bio', 'date_of_birth', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'profile_picture', 'bio', 'date_of_birth', 'phone_number')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(StatusUpdate)
admin.site.register(UserProfile)
