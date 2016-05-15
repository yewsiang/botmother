'''
import sys
import time
import pprint
import telepot

def handle(msg):
    pprint.pprint(msg)
    # Do your stuff here ...


# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]

# bot = telepot.Bot("228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A")
bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
'''
import sys
import time
import telepot
import pprint

TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'
bot = telepot.Bot(TOKEN)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print (content_type, chat_type, chat_id)
    if (content_type == "text"):
        show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
        bot.sendMessage(chat_id, "Bro, you just sent me a " +
                        content_type + "?", reply_markup=show_keyboard)
    else:
        bot.sendMessage(chat_id, "Bro, you sent something?")


bot.message_loop(handle)
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)