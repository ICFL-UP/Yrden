import logging
from action_provider import ActionProvider

logger = logging.getLogger('insert')


class Insert(ActionProvider):

    title = 'Insert'
    view = 'insert_detail'

    def perform(self, *args, **kwargs):
        logger.debug(
            'Insert::perform(): args:{}, kwargs:{}'.format(args, kwargs))

        print("Insert Action Perform()")
