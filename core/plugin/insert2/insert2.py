import logging
from action_provider import ActionProvider

logger = logging.getLogger('insert2')


class Insert2(ActionProvider):

    title = 'Insert2'
    view = 'insert2_detail'

    def perform(self, *args, **kwargs):
        logger.debug(
            'Insert2::perform(): args:{}, kwargs:{}'.format(args, kwargs))

        print("Insert2 Action Perform()\n")
