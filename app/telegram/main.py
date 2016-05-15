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
            print '%d. %s %s' % (self._qindex, self.QUESTIONS[self._qindex], answer)

        # Advance index to next question
        self._qindex += 1

        # Send question to user, or tell him no more questions.
        if self._qindex < len(self.QUESTIONS):
            self.sender.sendMessage(self.QUESTIONS[self._qindex])
        else:
            self.sender.sendMessage('No more questions. I am done.')


bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Questioner, timeout=20)),
])
bot.message_loop(run_forever=True)
