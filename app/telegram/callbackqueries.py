import telepot
from telepot.delegate import per_chat_id, create_open
from app.accounts import TelegramAccountManager


class CallbackQueries:
    # This class handles the callback functions
    @classmethod
    def question_answered(cls, bot, query_id):
        print "Question received by callback function!"
        print "This is query_id: " + query_id
        #
        # BOT EXPIRES WHEN SESSION EXPIRES
        #
        bot.sender.sendMessage("Question received by callback function!")
        # bot = telepot.bot(TOKEN)
