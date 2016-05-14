import sys
from flask import Flask
import telepot
from pprint import pprint


"""
$ python2.7 webhook_flask_skeleton.py <token> <listening_port> <webhook_url>
Webhook path is '/abc' (see below), therefore:
<webhook_url>: https://<base>/abc
"""


'''
TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]
'''
TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'
PORT = 8443
URL = '/telegram'

app = Flask(__name__)
bot = telepot.Bot(TOKEN)


def handle(message):
    pprint(message)

bot.message_loop(handle)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(port=PORT, debug=True)
    print "hi"
