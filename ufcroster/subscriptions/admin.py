from django.contrib import admin

from .models import Notification, Subscription


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created', 'type', 'response_id')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
