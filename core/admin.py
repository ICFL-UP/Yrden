from django.contrib import admin

from .models import Plugin, PluginSource


class PluginInline(admin.TabularInline):
    model = Plugin
    fk_name = 'plugin_source'

@admin.register(PluginSource)
class PluginSourceAdmin(admin.ModelAdmin):
    inlines = [
        PluginInline
    ]
