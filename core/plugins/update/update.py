from action_provider import ActionProvider

class Update(ActionProvider):

    title = 'Update'
    view = 'update_detail'

    def perform(self):
        print("Update Action Perform()")