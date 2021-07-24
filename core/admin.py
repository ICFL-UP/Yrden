from django.contrib import admin

from .models import Plugin


class PluginAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['name', 'interval', 'should_run']}),
        ('Last Run Time',   {'fields': ['last_run_datetime']}),
    ]

    list_display = ('name', 'interval', 'last_run_datetime', 'should_run')
    search_fields = ['name']


admin.site.register(Plugin, PluginAdmin)
