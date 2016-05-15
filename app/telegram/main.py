import telepot
import pprint
from telepot.delegate import per_chat_id, create_open

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


class Command:
    @classmethod
    def processCommand(cls, bot, command):
        channelExists = bot.user_details.channelExists
        # NOT DOOONE: UNIMPLEMENTED COMMANDS
        if command == '/help':
            print 'You need help. Eh?'
            bot.sender.sendMessage('You need help. Eh?')

        elif command == '/me':
            if not channelExists:
                bot.sender.sendMessage('You have not subscribed to any mods')
            else:
                bot.sender.sendMessage('Your modules subscribed are ...')

        elif command == '/modules':
            bot.sender.sendMessage(
                'These are the modules that you can subscribe to ...')

        elif command == '/add':
            # May remove this. Let people add mods directly (Eg "/MA1234")
            bot.sender.sendMessage('What module would you like to add?')

        elif command == '/delete':
            if not channelExists:
                bot.sender.sendMessage('You have not subscribed to any mods')
            else:
                bot.sender.sendMessage('What module would you like to delete?')

        else:
            # Say people do this "/MA1234"
            # We must search if "MA1234" is a valid module
            moduleCode = command[1:]
            # moduleExists = checkIfModuleExists(moduleCode)
            moduleExists = True
            if (moduleExists):
                bot.user_details.joinChannels(moduleCode)
            else:
                bot.sender.sendMessage('Mod does not exist. Check /modules to see the available modules')
            bot.sender.sendMessage('End of Adding module')
        return


class User:
    def __init__(self, bot, telegram_id):
        self.telegram_id = telegram_id
        self.channels = []
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
        self.channels.append(module_code)
        all_modules = ""
        for channel in self.channels:
            all_modules += (channel + " ")
        self.bot.sender.sendMessage("Joining channels")
        self.bot.sender.sendMessage("Joined " + all_modules)
        return


# Starting up the bot
class Start(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Start, self).__init__(seed_tuple, timeout)
        # Admin checks every time the bot has been initialized
        # If user is not registered in db, register him
        # If user does not have any channels, set channelExists = False
        telegram_id = seed_tuple[2]
        self.user_details = User(self, telegram_id)

        userExists = self.user_details.checkUserAccount()
        if not userExists:
            self.user_details.createUserAccount()

        self.user_details.channelExists = self.user_details.checkChannels()

        print "-- Initialization --"

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self.sender.sendMessage("Please key in a text command :)")
            return

        command = msg['text'].strip().lower()
        Command.processCommand(self, command)

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            self.sender.sendMessage('Session expired')


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Start, timeout=20)),
])
bot.message_loop(run_forever=True)
