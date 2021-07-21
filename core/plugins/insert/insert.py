from action_provider import ActionProvider

class Insert(ActionProvider):

    title = 'Insert'
    view = 'insert_detail'

    def perform(self):
        print("Insert Action Perform()")