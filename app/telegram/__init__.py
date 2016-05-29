import telepot
from telepot.delegate import per_application, per_chat_id, create_open
from .commands import Command, State
from .callbackqueries import CallbackQueries
from app.accounts import TelegramAccountManager

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


# There will only be 1 CallbackBot in the application
# The Bot handles callback_queries when users click on inline keyboard buttons
class CallbackBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(CallbackBot, self).__init__(seed_tuple, timeout)

    def on_callback_query(self, msg):
        print "----- ON CALLBACK QUERY!!! -----"
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')

        if data == 'notification':
            CallbackQueries.question_answered(self, query_id)
            bot.answerCallbackQuery(query_id, text='Question sent to be voted!')

    # CallbackBot should only be handling Callback queries and nothing else.
    def on_chat_message(self, msg):
        return


# Starting up the bot
class MainBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MainBot, self).__init__(seed_tuple, timeout)
        # Admin checks every time the bot has been initialized
        # If user is not registered in db, register him
        # If user does not have any channels, set channelExists = False
        telegram_id = seed_tuple[2]
        self.telegram_id = telegram_id
        self.state = State.NORMAL
        TelegramAccountManager.create_account_if_does_not_exist(telegram_id)
        print "---- INITIALIZATION ----"

    def on_chat_message(self, msg):
        print "-- On_chat_message --"
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self.sender.sendMessage("Please key in a text command :)")
            return

        command = msg['text'].strip().lower()
        Command.process_commands(self, command)

    # Callback_query will be answered by CallbackBot. MainBot ignores such queries.
    def on_callback_query(self, msg):
        return

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            print "---- Session Expired ----"
            self.sender.sendMessage('Session expired')


bot = telepot.DelegatorBot(TOKEN, [
    #
    # IMPORTANT: CallbackBot will not work if the program has been closed. You need one message to init it.
    # Assumption that timeout=None means the Bot will run forever
    # Note also: the message will run through CallbackBot first and then to MyBot
    #
    (per_application(), create_open(CallbackBot, timeout=None)),
    (per_chat_id(), create_open(MainBot, timeout=20)),
])
# cannot put bot.message_loop() here or there will be a bug
