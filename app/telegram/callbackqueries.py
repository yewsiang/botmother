import telepot
from telepot.delegate import per_chat_id, create_open
from app.accounts import TelegramAccountManager


class CallbackQueries:
    '''
    This class handles the callback functions.
    The "data" variable will encode the information.
    The "delegator_bot" is to allow notifications on the top of the screen.
    '''
    @classmethod
    def on_answer(cls, bot, delegator_bot, data, query_id):
        # All callback queries will pass through this function and be allocated to
        # a suitable function to handle it based on information in "data"
        #
        # TODO: Data may have uneven lengths.
        # Encoded information be in the first 5 letters?
        #
        print "Data: " + data
        if data == 'question_answered':
            CallbackQueries.question_answered(bot, delegator_bot, data, query_id)
        elif data == 'voted':
            #
            # TODO: Support other callback queries
            #
            print 'Wat'

    @classmethod
    def question_answered(cls, bot, delegator_bot, data, query_id):
        #
        # BOT EXPIRES WHEN SESSION EXPIRES
        #
        bot.sender.sendMessage("This is data : " + data)
        bot.sender.sendMessage("Question received by callback function!")
        delegator_bot.answerCallbackQuery(query_id, text='Question sent to be voted!')
        # bot = telepot.bot(TOKEN)
