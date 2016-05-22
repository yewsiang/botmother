"""
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
'''
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
'''

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
'''

from telepot.delegate import per_chat_id_in, per_application, call, create_open

'''
$ python3.5 chatbox_nodb.py <token> <owner_id>
Chatbox - a mailbox for chats
1. People send messages to your bot.
2. Your bot remembers the messages.
3. You read the messages later.
This version only stores the messages in memory. If the bot is killed, all messages are lost.
This version only handles text messages.
It accepts the following commands from you, the owner, only:
- /unread - tells you who has sent you messages and how many
- /next - read next sender's messages
It can be a starting point for customer-support type of bots.
'''

# Simulate a database to store unread messages


class UnreadStore(object):
    def __init__(self):
        self._db = {}

    def put(self, msg):
        chat_id = msg['chat']['id']

        if chat_id not in self._db:
            self._db[chat_id] = []

        self._db[chat_id].append(msg)

    # Pull all unread messages of a `chat_id`
    def pull(self, chat_id):
        messages = self._db[chat_id]
        del self._db[chat_id]

        # sort by date
        messages.sort(key=lambda m: m['date'])
        return messages

    # Tells how many unread messages per chat_id
    def unread_per_chat(self):
        return [(k, len(v)) for k, v in self._db.items()]


# Accept commands from owner. Give him unread messages.
class OwnerHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout, store):
        super(OwnerHandler, self).__init__(seed_tuple, timeout)
        self._store = store

    def _read_messages(self, messages):
        for msg in messages:
            # assume all messages are text
            self.sender.sendMessage(msg['text'])

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self.sender.sendMessage("I don't understand")
            return

        command = msg['text'].strip().lower()

        # Tells who has sent you how many messages
        if command == '/unread':
            results = self._store.unread_per_chat()

            lines = []
            for r in results:
                n = 'ID: %d\n%d unread' % r
                lines.append(n)

            if not len(lines):
                self.sender.sendMessage('No unread messages')
            else:
                self.sender.sendMessage('\n'.join(lines))

        # read next sender's messages
        elif command == '/next':
            results = self._store.unread_per_chat()

            if not len(results):
                self.sender.sendMessage('No unread messages')
                return

            chat_id = results[0][0]
            unread_messages = self._store.pull(chat_id)

            self.sender.sendMessage('From ID: %d' % chat_id)
            self._read_messages(unread_messages)

        else:
            self.sender.sendMessage("I don't understand")


class MessageSaver(telepot.helper.Monitor):
    def __init__(self, seed_tuple, store, exclude):
        # The `capture` criteria means to capture all messages.
        super(MessageSaver, self).__init__(
            seed_tuple, capture=[{'_': lambda msg: True}])
        self._store = store
        self._exclude = exclude

    # Store every message, except those whose sender is in the exclude list,
    # or non-text messages.
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if chat_id in self._exclude:
            print('Chat id %d is excluded.' % chat_id)
            return

        if content_type != 'text':
            print('Content type %s is ignored.' % content_type)
            return

        print('Storing message: %s' % msg)
        self._store.put(msg)


import threading


class CustomThread(threading.Thread):
    def start(self):
        print('CustomThread starting ...')
        super(CustomThread, self).start()

# Note how this function wraps around the `call()` function below to implement
# a custom thread for delegation.


def custom_thread(func):
    def f(seed_tuple):
        target = func(seed_tuple)

        if type(target) is tuple:
            run, args, kwargs = target
            t = CustomThread(target=run, args=args, kwargs=kwargs)
        else:
            t = CustomThread(target=target)

        return t
    return f


class ChatBox(telepot.DelegatorBot):
    def __init__(self, token, owner_id):
        self._owner_id = owner_id
        self._seen = set()
        self._store = UnreadStore()

        super(ChatBox, self).__init__(token, [
            # Here is a delegate to specially handle owner commands.
            (per_chat_id_in([owner_id]), create_open(
                OwnerHandler, 20, self._store)),

            # Only one MessageSaver is ever spawned for entire application.
            (per_application(), create_open(
                MessageSaver, self._store, exclude=[owner_id])),

            # For senders never seen before, send him a welcome message.
            (self._is_newcomer, custom_thread(call(self._send_welcome))),
        ])

    # seed-calculating function: use returned value to indicate whether to
    # spawn a delegate
    def _is_newcomer(self, msg):
        chat_id = msg['chat']['id']
        if chat_id == self._owner_id:  # Sender is owner
            return None  # No delegate spawned

        if chat_id in self._seen:  # Sender has been seen before
            return None  # No delegate spawned

        self._seen.add(chat_id)
        # non-hashable ==> delegates are independent, no seed association is
        # made.
        return []

    def _send_welcome(self, seed_tuple):
        chat_id = seed_tuple[1]['chat']['id']

        print('Sending welcome ...')
        self.sendMessage(chat_id, 'Hello!')

OWNER_ID = str(45369113)

bot = ChatBox(TOKEN, OWNER_ID)
bot.message_loop(run_forever=True)
"""
