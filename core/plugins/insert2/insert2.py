from action_provider import ActionProvider

class Insert2(ActionProvider):

    title = 'Insert2'
    view = 'insert2_detail'

    def perform(self):
        print("Insert2 Action Perform()")