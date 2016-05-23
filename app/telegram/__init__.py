import telepot
from telepot.delegate import per_chat_id, create_open
from .commands import Command, State
from app.accounts import TelegramAccountManager

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


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

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            print "Session Expired"
            self.sender.sendMessage('Session expired')


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Start, timeout=20)),
])
