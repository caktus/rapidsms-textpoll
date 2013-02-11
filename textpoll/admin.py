from django.contrib import admin
from textpoll import models as textpoll


class OptionAdmin(admin.TabularInline):
    model = textpoll.Option


class PollAdmin(admin.ModelAdmin):
    inlines = (OptionAdmin,)
    list_display = ('slug', 'text', 'active')
    list_filter = ('active',)
    ordering = ('slug',)
    search_fields = ('slug', 'text')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'connection', 'date', 'text')
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('poll__slug', 'poll__text', 'connection__identity')
    raw_id_fields = ('poll', 'connection', 'option')


admin.site.register(textpoll.Poll, PollAdmin)
admin.site.register(textpoll.Vote, VoteAdmin)
