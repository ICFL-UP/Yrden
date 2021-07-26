from .plugin_mount_type import PluginMountType


class PluginMount(metaclass=PluginMountType):
    """
    Mount point for plugins.

    The mount point is a singleton so that multiple instances of the
    mount point does not accidentally get created. This ensures that
    there are only one copy of each plugin within the system.
    """

    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance
        else:
            inst = cls.instance = super(PluginMount, cls).__new__(cls)
            return inst
