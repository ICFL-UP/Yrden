import logging
from action_provider import ActionProvider

logger = logging.getLogger('update')


class Update(ActionProvider):

    title = 'Update'
    view = 'update_detail'

    def perform(self, *args, **kwargs):
        logger.debug(
            'Update::perform(): args:{}, kwargs:{}'.format(args, kwargs))

        print("Update Action Perform()\n")
