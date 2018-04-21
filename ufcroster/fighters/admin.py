from django.contrib import admin

from .models import Fighter, FighterRecord, FighterUrls, FightDetails, Fight


class FighterUrlsInline(admin.StackedInline):
    model = FighterUrls


class FighterRecordInline(admin.StackedInline):
    model = FighterRecord


class FighterAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'in_ufc', 'country', 'created')
    list_filter = ('country',)
    ordering = ['-active']
    inlines = [FighterUrlsInline, FighterRecordInline]


class FightDetailsAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'status', 'event', 'created', 'modified')
    list_select_related = ('event', )


class FightAdmin(admin.ModelAdmin):
    list_display = ('fighter', 'result', 'opponent', 'created', 'modified')
    list_select_related = ('fighter', 'opponent', 'details')
    search_fields = ('fighter__name', 'fighter__slug',)


admin.site.register(Fighter, FighterAdmin)
admin.site.register(FightDetails, FightDetailsAdmin)
admin.site.register(Fight, FightAdmin)
