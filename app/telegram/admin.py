from .commands import State
from telepot.namedtuple import ReplyKeyboardHide


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
            bot.sender.sendMessage("<b>NUS Question Bot</b>\n"
                "/ask - <b>Ask questions</b> about specific modules!\n"  # Changes state
                "/me - Modules that you have subscribed to\n"
                "/modules -Modules to join!\n"
                "/&lt;module code&gt; - Add a module\n(E.g /MOM1000)\n"
                "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                "/settings - Change your settings (E.g notification rate)\n"  # Changes state
                "/help - Help :)\n\n"
                "Also, look out for questions by your peers after you've subscribed to a module!",
                parse_mode='HTML')
        elif (bot.state == State.DELETING_CHANNEL):
            bot.sender.sendMessage("/<module code> - Delete a module that you are subscribed to\n"
                "/done - Done with deleting modules\n")
        elif (bot.state == State.ASKING_QUESTIONS):
            bot.sender.sendMessage("Send a question to those who are subscribed to the particular module\n"
                "/done - Done with asking questions\n")
        elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
            bot.sender.sendMessage("/<module code> - Send the question that you've asked to the people "
                "subscribed to this particular module\n"
                "/done - Done with asking questions\n")
        elif (bot.state == State.ANSWERING_QUESTIONS):
            bot.sender.sendMessage("Just type your answer to the question :)!\n"
                "/done - Go back\n")
        elif (bot.state == State.VOTING):
            bot.sender.sendMessage("Choose one of the answers that you're most confident of."
                "Please choose carefully as there are others learning from your votes :)\n"
                "/done - Go back\n")
        elif (bot.state == State.CHANGE_SETTINGS):
            bot.sender.sendMessage("Change your settings over here\n"
                "/messagesperday - Change number of messages we send to you per day\n"
                "/done - Go back\n")
        else:
            print "ERROR: There should not be any other states other than those listed"


class Admin:
    '''
    This class handles the administrative commands by the User.
    Such as /done, /start, /restart
    '''
    # /start or /restart - When User starts using the bot
    @classmethod
    def start_command(cls, bot):
        bot.sender.sendMessage("Welcome to NUS Question Bot! Ask questions and answer questions on the go!\n")
        bot.state = State.NORMAL
        Help.help_according_to_state(bot)

    # /done - When User types /done in any State
    @classmethod
    def done_command(cls, bot):
        bot.state = State.NORMAL
        bot.sender.sendMessage("Done :)! /help for help!", reply_markup=ReplyKeyboardHide(hide_keyboard=True))

    # User probably typed something invalid
    @classmethod
    def invalid_command(cls, bot):
        bot.sender.sendMessage("You're not allowed to do this.\n/help for help :)")
