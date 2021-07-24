import logging
from ..plugin_mount import PluginMount

logger = logging.getLogger('insert')


class Insert(PluginMount):

    title = 'Insert'
    view = 'insert_detail'

    def perform(self, *args, **kwargs):
        logger.debug(
            'Insert::perform(): args:{}, kwargs:{}'.format(args, kwargs))

        print("Insert Action Perform()\n")
