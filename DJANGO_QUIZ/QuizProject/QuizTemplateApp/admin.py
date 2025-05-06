from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'is_superuser']
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Authentication', {
            'fields': ('password',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        if not obj:  # If creating a new user
            return True
        if obj.is_superuser:  # No one can edit superusers
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_staff:
            return False
        if not obj:  # If deleting a new user
            return True
        if obj.is_superuser:  # No one can delete superusers
            return False
        return True

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user
            obj.set_password(form.cleaned_data['password'])
        elif 'password' in form.changed_data:  # If password is being changed
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
