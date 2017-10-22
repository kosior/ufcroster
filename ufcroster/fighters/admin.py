from django.contrib import admin

from .models import Fighter, FighterUrls


class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'in_ufc')


class FighterUrlsAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'ufc', 'sherdog')


admin.site.register(Fighter, FighterAdmin)
admin.site.register(FighterUrls, FighterUrlsAdmin)
