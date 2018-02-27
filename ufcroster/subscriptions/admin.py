from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created', 'type', 'response_id')


admin.site.register(Notification, NotificationAdmin)
