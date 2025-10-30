from django.contrib import admin
from .models import Notifications
@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_date', 'status', 'type', 'read_at')
    search_fields = ('user__email', 'message', 'reference_id')
    list_filter = ('status', 'type', 'created_date')
