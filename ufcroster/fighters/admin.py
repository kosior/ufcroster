from django.contrib import admin

from .models import Fighter, FighterRecord, FighterUrls, FightDetails, Fight


class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'in_ufc', 'country', 'created')
    list_filter = ('country',)


class FighterRecordAdmin(admin.ModelAdmin):
    list_display = ('fighter', )


class FighterUrlsAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'ufc', 'sherdog')


class FightDetailsAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'status', 'event', 'created', 'modified')
    list_select_related = ('event', )


class FightAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'result', 'opponent', 'created', 'modified')
    list_select_related = ('fighter', 'opponent', 'details')
    search_fields = ('fighter__name', 'fighter__slug',)


admin.site.register(Fighter, FighterAdmin)
admin.site.register(FighterRecord, FighterRecordAdmin)
admin.site.register(FighterUrls, FighterUrlsAdmin)
admin.site.register(FightDetails, FightDetailsAdmin)
admin.site.register(Fight, FightAdmin)
