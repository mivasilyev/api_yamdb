from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('bio', 'role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_editable = ('role',)
    list_filter = UserAdmin.list_filter + ('role',)

admin.site.register(MyUser, CustomUserAdmin)