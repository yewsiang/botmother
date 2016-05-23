import telepot
from telepot.delegate import per_chat_id, create_open
from .commands import Command, State
from .callbackqueries import CallbackQueries
from app.accounts import TelegramAccountManager

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'

message_with_inline_keyboard = None


# Starting up the bot
class Start(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Start, self).__init__(seed_tuple, timeout)
        # Admin checks every time the bot has been initialized
        # If user is not registered in db, register him
        # If user does not have any channels, set channelExists = False
        print "START"
        telegram_id = seed_tuple[2]
        self.telegram_id = telegram_id
        self.state = State.NORMAL
        print "telegram_id" + str(telegram_id)
        userExists = TelegramAccountManager.create_account_if_does_not_exist(telegram_id)
        print userExists

        # self.user_details.channelExists = self.user_details.checkChannels()

        print "-- INITIALIZATION --"

    def on_chat_message(self, msg):
        print "On chat message"
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self.sender.sendMessage("Please key in a text command :)")
            return

        command = msg['text'].strip().lower()
        Command.process_commands(self, command)

    # TEST
    # usage of "bot" seems a bit hacky
    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        print 'Callback query:', query_id, from_id, data

        if data == 'notification':
            CallbackQueries.question_answered(self, query_id)
            bot.answerCallbackQuery(query_id, text='Question sent to be voted!')
        return
    #
    #

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            print "Session Expired"
            self.sender.sendMessage('Session expired')


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Start, timeout=20)),
])
