from .commands import State


class Help:
    '''
    This class handles all the /help commands by the User.
    Note: Different help replies are given depending on the State of the User.
    '''
    # /help - When User types /help in any State
    @classmethod
    def help_according_to_state(cls, bot):
        # DEPENDING on the STATE of the User, provide different help commands
        #
        # TODO
        #
        if bot.state == State.NORMAL:
            bot.sender.sendMessage("NUS Question Bot\n"
                "/help - List commands that you can\n"
                "/me - List the modules that you are subscribed to\n"
                "/ask - Ask questions!\n"  # Changes state
                "/modules - List the modules that you can subscribe to\n"
                "/<module code> - Add a module (E.g /MOM1000 adds the module MOM1000)\n"
                "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                "/settings - Change your settings (E.g notification rate)")  # Changes state
        elif (bot.state == State.DELETING_CHANNEL):
            bot.sender.sendMessage("/<module code> - Delete a module that you are subscribed to\n"
                "/done - Done with deleting modules\n")
        elif (bot.state == State.ASKING_QUESTIONS):
            bot.sender.sendMessage("Send a question to those who are subscribed to the particular module\n"
                "/done - Done with asking questions\n")
        elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
            bot.sender.sendMessage("/<module code> - Send the question that you've asked to the people"
                "subscribed to this particular module\n")
        elif (bot.state == State.ANSWERING_QUESTIONS):
            bot.sender.sendMessage("/help for ANSWERING_QUESTIONS")
        elif (bot.state == State.VOTING):
            bot.sender.sendMessage("/help for VOTING")
        elif (bot.state == State.CHANGE_SETTINGS):
            bot.sender.sendMessage("/help for CHANGE_SETTINGS")
        else:
            print "ERROR: There should not be any other states other than those listed"
