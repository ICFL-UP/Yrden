class PluginMount(type):
    """
    Defines a mount point for all plugins in the system.
    Adding a new plugin registers the plugin within this class.

    Can then loop over the list of plugins in the class and:
    - Run the plugin module
    - Skip the plugin module
    """

    def __init__(cls, name, base, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)