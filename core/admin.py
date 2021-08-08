from django.contrib import admin

from .models import Plugin


class PluginAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['username', 'name', 'hash_name', 'interval', 'should_run', 'plugin_dest']}),
        ('Last Run Time',   {'fields': ['last_run_datetime']}),
    ]

    list_display = ('username', 'name', 'hash_name', 'interval', 'last_run_datetime', 'should_run', 'plugin_dest')
    search_fields = ['name']


admin.site.register(Plugin, PluginAdmin)
