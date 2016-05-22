import telepot
from telepot.delegate import per_chat_id, create_open
from .commands import Command, State
from app.accounts import TelegramAccountManager
import pprint

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


class UserDetails:
    def __init__(self, bot, telegram_id):
        self.telegram_id = telegram_id
        self.channels = []
        self.channelExists = False
        self.bot = bot
        self.bot.sender.sendMessage("Creating the USER class")

    def getTelegramID(self):
        self.bot.sender.sendMessage("Getting your telegram_id")
        return self.telegram_id

    def getChannels(self):
        # Retrieve the channels that the user is subscribed to
        self.bot.sender.sendMessage("Getting your channels")
        return self.channels

    def checkUserAccount(self):
        # NOT DOOONE:
        # use self.telegram_id to check
        # Check if this users' telegram userid exists, return boolean
        self.bot.sender.sendMessage("Checking your account")
        return True

    def createUserAccount(self):
        # NOT DOOONE:
        # use self.telegram_id to create
        # Create a user account with this particular telegram id
        self.bot.sender.sendMessage("Creating your account")
        return

    def checkChannels(self):
        # NOT DOOONE:
        # use self.telegram_id to get the channels
        # Retrieve the channels that the user is subscribed to, return boolean
        self.bot.sender.sendMessage(
            "Checking the modules that you've subscribed")
        self.channels = ["WA123456789"]
        return False

    def joinChannels(self, module_code):
        # NOT DOOONE:
        # use module_code to select the channel to join
        # change channelExists accordingly
        # if (module_code exists):
        self.channels.append(module_code)
        all_modules = ""
        for channel in self.channels:
            all_modules += (channel + " ")
        self.bot.sender.sendMessage("Joining channels")
        self.bot.sender.sendMessage("Joined " + all_modules)
        self.channelExists = True
        # else:
        #   self.bot.sender.sendMessage("I'm sorry the module does not exist")
        return


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
