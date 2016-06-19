import telepot
from telepot.delegate import per_application, per_chat_id, create_open
from .commands import Command, State
from pprint import pprint
from .callbackqueries import CallbackQueries
from app.accounts import TelegramAccountManager

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'

# Left here in case we want to implement such a method in the future
"""
class CallbackBot(telepot.helper.ChatHandler):
    '''
    There will only be 1 CallbackBot in the entire application.
    The Bot handles callback_queries when users click on inline keyboard buttons.
    This will be the Bot that all queries will pass through first. If it is not a callback query,
    it will simply return and MainBot will takeover the handling of the message.
    '''
    def __init__(self, seed_tuple, timeout):
        super(CallbackBot, self).__init__(seed_tuple, timeout)
        print "---- INIT OF CALLBACKBOT ----"

    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        print "---- CALLBACK QUERY ----"
        CallbackQueries.on_answer(self, bot, data, query_id)

    # CallbackBot should only be handling Callback queries and nothing else.
    def on_chat_message(self, msg):
        return

    def on_close(self, exception):
        print "----- CALLBACK BOT CLOSED ----- THIS SHOULD NOT BE HAPPENING --------"
"""


class MainBot(telepot.helper.ChatHandler):
    '''
    There will be 1 MainBot for EVERY USER.
    This Bot will maintain the state of the user while the session hasn't expired.
    This Bot is responsible for all the non-callback queries to the Bot.
    '''
    def __init__(self, seed_tuple, timeout):
        super(MainBot, self).__init__(seed_tuple, timeout)
        # Admin checks every time the bot has been initialized.
        # If user is not registered in db, register him. Initialize state to NORMAL.
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

        Command.process_commands(self, bot, msg)

    '''
    # Callback_query will be answered by CallbackBot. MainBot ignores such queries.
    def on_callback_query(self, msg):
        return
    '''

    def on_callback_query(self, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        print "---- CALLBACK QUERY ----"
        CallbackQueries.on_answer(self, bot, data, query_id, msg['message']['message_id'])

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            print "---- SESSION EXPIRED ----"
            self.sender.sendMessage('Session expired')


bot = telepot.DelegatorBot(TOKEN, [
    #
    # IMPORTANT: CallbackBot will NOT WORK if the program has been closed. You need one message to init it.
    # Assumption that timeout=None means the Bot will run forever
    # Note also: the message will run through CallbackBot first and then to MyBot
    #
    # (per_application(), create_open(CallbackBot, timeout=None)),
    (per_chat_id(), create_open(MainBot, timeout=None)),
])
# CANNOT put bot.message_loop() here or there will be a bug
