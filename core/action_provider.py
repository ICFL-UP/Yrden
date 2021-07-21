from plugin_mount import PluginMount

class ActionProvider(metaclass=PluginMount):
    """
    Mount point for plugins which refer to actions that can be performed.

    Plugins implementing this reference should provide the following attributes:

    ========  ========================================================
    title     The text to be displayed, describing the action

    url       The URL to the view where the action will be carried out
    ========  ========================================================
    """

    def get_plugins(cls, *args, **kwargs):
        return [p(*args, **kwargs) for p in cls.plugins]