import telepot
import pprint
from telepot.delegate import per_chat_id, create_open

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


# Questioner class
class Questioner(telepot.helper.ChatHandler):
    QUESTIONS = [
        'What is your name?',
        'How old are you?',
    ]

    def __init__(self, seed_tuple, timeout):
        super(Questioner, self).__init__(seed_tuple, timeout)
        print (seed_tuple)

        # Remember which question you are asking
        self._qindex = -1

    def on_chat_message(self, msg):
        # Display answer to your questions
        if 0 <= self._qindex < len(self.QUESTIONS):
            answer = msg['text']
            print '%d. %s %s' % (
                self._qindex, self.QUESTIONS[self._qindex], answer)

        # Advance index to next question
        self._qindex += 1

        # Send question to user, or tell him no more questions.
        if self._qindex < len(self.QUESTIONS):
            self.sender.sendMessage(self.QUESTIONS[self._qindex])
        else:
            self.sender.sendMessage('No more questions. I am done.')


class Account:
    # initialize user_id to -1
    def __init__(self):
        self.user_id = -1

    def getUserID(self):
        return self.user_id

    def checkUserAccount(self):
        # GET request to find out if account with this telegram userid exists
        self.user_id = 1
        return True

    def createUserAccount(self):
        # POST request to create a user account with this particular userid
        return


class Channel:
    def __init__(self):
        self.channels = []

    def getChannels(self):
        return self.channels

    def checkChannels(self):
        # GET request to find out the channels that the user is subscribed to
        self.channels = ["WA1234"]
        return True

    def joinChannels(self):
        return


# Starting up the bot
class Start(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Start, self).__init__(seed_tuple, timeout)
        # Check if the user has an account
        userExists = Account.checkUserAccount(self)
        if userExists:
            channelExists = Channel.checkChannels(self)
        else:
            Account.createUserAccount(self)

    def on_chat_message(self, msg):
        return


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Start, timeout=20)),
])
bot.message_loop(run_forever=True)
