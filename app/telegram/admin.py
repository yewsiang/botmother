import emoji
from .commands import State
from .points import Points, Badges
from telepot.namedtuple import ReplyKeyboardHide
from app.accounts import TelegramAccountManager


class Help:
    '''
    This class handles all the /help commands by the User.
    Note: Different help replies are given depending on the State of the User.
    '''
    # /help - When User types /help in any State
    @classmethod
    def help_according_to_state(cls, bot):
        # Address User by his title
        title, points_to_next_level = Points.get_title(bot)

        # DEPENDING on the STATE of the User, provide different help commands
        if bot.state == State.NORMAL:
            # Badges.print_badges()
            bot.sender.sendMessage(emoji.emojize("<b>NUS Question Bot :thumbs_up_sign:</b>\n\n"
                "Dear <b>" + title[1] + "</b>" + title[2] + ",\n"
                "/ask - <b>Ask questions</b> about specific modules!\n"  # Changes state
                "/me - Modules that you have subscribed to\n"
                "/modules - Modules to join!\n"
                "/&lt;module code&gt; - Add a module\n(E.g /CS1010)\n"
                "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                "/points - Get your points & badges\n"
                # "/settings - Change your settings (E.g notification rate)\n"  # Changes state
                "/verify - Receive a One-Time Password to register a web account\n"
                "/help - Help :)\n\n"
                "Also, look out for questions by your peers after you've subscribed to a module!",
                use_aliases=True), parse_mode='HTML')
        elif (bot.state == State.SELECTING_FACULTY):
            bot.sender.sendMessage("/<faculty> - Show the modules within the faculty\n"
                "/<module code> - Add a module\n(E.g /CS1010)\n"
                "/done - Done with browsing modules\n")
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
                "/messagesperday - Change maximum number of messages we send to you per day\n"
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
        bot.state = State.NORMAL
        Help.help_according_to_state(bot)
        bot.sender.sendMessage("Welcome to NUS Question Bot!\n"
            "<b>Ask questions</b> and <b>answer questions</b> on the go!\n\n"
            "You can start by subscribing to modules at /modules\n\n"
            "If you need help, just /help :)", parse_mode='HTML')

    # /verify - When User types /verify - will generate a one-time password and send it to them. Also sets it in their user object
    @classmethod
    def verify_command(cls, bot):
        otp = TelegramAccountManager.generate_and_store_otp(bot.telegram_id)
        bot.sender.sendMessage("Your One-Time Password for registration is " + str(otp))

    # /done - When User types /done in any State
    @classmethod
    def done_command(cls, bot):
        bot.state = State.NORMAL
        bot.sender.sendMessage("Done :)! /help for help!", reply_markup=ReplyKeyboardHide(hide_keyboard=True))

    # User probably typed something invalid
    @classmethod
    def invalid_command(cls, bot):
        bot.sender.sendMessage("You're not allowed to do this.\n/help for help :)")
