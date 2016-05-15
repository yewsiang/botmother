import sys
import time
import telepot
import pprint

from pprint import pprint
TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'

'''
bot = telepot.Bot(TOKEN)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print (content_type, chat_type, chat_id)
    if (content_type == "text"):
        show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
        bot.sendMessage(chat_id, "Bro, you just sent me a " +
                        content_type + "?", reply_markup=show_keyboard)

        # How do I store the user's reply here so that I can print it
        # Need to learn how to echo?

        hide_keyboard = {'hide_keyboard': True}
        bot.sendMessage(chat_id, "Im hiding the keyboard",
                        reply_markup=hide_keyboard)
    else:
        bot.sendMessage(chat_id, "Bro, you sent something?")


bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
'''

# Message counter
"""
from telepot.delegate import per_chat_id, create_open


class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_chat_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])

bot.message_loop(run_forever=True)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
"""

# Guess a number game
import random
import traceback
from telepot.delegate import per_chat_id, create_open
'''
class Player(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Player, self).__init__(seed_tuple, timeout)
        self._answer = random.randint(0, 99)

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    def open(self, initial_msg, seed):
        self.sender.sendMessage('Guess my number')
        pprint(vars(self))
        pprint(vars(telepot.helper.ChatHandler))
        return True
        # prevent on_message() from being called on the initial message

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self.sender.sendMessage('Give me a number, please.')
            return

        try:
            guess = int(msg['text'])
        except ValueError:
            self.sender.sendMessage('Give me a number, please.')
            return

        # check the guess against the answer ...
        if guess != self._answer:
            # give a descriptive hint
            hint = self._hint(self._answer, guess)
            self.sender.sendMessage(hint)
        else:
            self.sender.sendMessage('Correct!')
            self.close()

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            self.sender.sendMessage(
                'Game expired. The answer is %d' % self._answer)
'''

'''
class TestShit(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(TestShit, self).__init__(seed_tuple, timeout)
        print("---- Initialization ----")
        print(seed_tuple)
        print("Timeout is " + str(timeout))

    def _hint(self, answer, guess):
        print "Is this supposed to reply to my messages?"

    def open(self, initial_msg, seed):
        print "---- Open function ----"
        self.sender.sendMessage("Your seed is " + str(seed))
        return True  # To prevent on_chat_message from being exec

    def on_chat_message(self, msg):
        print "More hello worlds since you are talking to me!"

    def on_close(self, exception):
        if isinstance(exception, telepot.exception.WaitTooLong):
            self.sender.sendMessage(
                'Expired. Try again')
        print "--------- Closed ---------"
'''


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
