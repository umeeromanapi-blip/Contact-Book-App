from django.contrib import admin
from .models import Contact, ActivityLog


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'category', 'user', 'is_favorite', 'created_at')
    search_fields = ('name', 'phone', 'email', 'notes')
    list_filter = ('category', 'is_favorite', 'created_at', 'user')
    ordering = ('-id',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'description', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    ordering = ('-created_at',)
