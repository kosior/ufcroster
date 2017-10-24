from django.contrib import admin

from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')


admin.site.register(Event, EventAdmin)