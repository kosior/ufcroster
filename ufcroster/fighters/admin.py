from django.contrib import admin

from .models import Fighter, FighterRecord, FighterUrls, FightDetails, Fight


class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'in_ufc')


class FighterRecordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'wins', 'losses', 'draws', 'nc')


class FighterUrlsAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'ufc', 'sherdog')


class FightDetailsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'event', 'type')


class FightAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'result', 'opponent')


admin.site.register(Fighter, FighterAdmin)
admin.site.register(FighterRecord, FighterRecordAdmin)
admin.site.register(FighterUrls, FighterUrlsAdmin)
admin.site.register(FightDetails, FightDetailsAdmin)
admin.site.register(Fight, FightAdmin)
