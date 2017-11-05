from django.contrib import admin

from .models import Fighter, FighterRecord, FighterUrls, FullFight, PartFight


class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'in_ufc')


class FighterRecordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'wins', 'losses', 'draws', 'nc')


class FighterUrlsAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'ufc', 'sherdog')


class FullFightAdmin(admin.ModelAdmin):
    list_display = ('part_1', 'part_2', 'event', 'type', 'status')


class PartFightAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'result', 'opponent')


admin.site.register(Fighter, FighterAdmin)
admin.site.register(FighterRecord, FighterRecordAdmin)
admin.site.register(FighterUrls, FighterUrlsAdmin)
admin.site.register(FullFight, FullFightAdmin)
admin.site.register(PartFight, PartFightAdmin)
