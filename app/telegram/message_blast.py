from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class MessageBlast:
    '''
    The MessageBlast class regulates situations when we have to send
    messages from one to many
    Possible Reasons:
    1) User asks question => question to be sent to those subscribed
    2) Question has been answered => answers to be sent to be voted
    3) Voting results are out + Asker's vote is out => Results to be
    sent to those who participated along with forum link
    '''
    @classmethod
    def send_question_to_answerers(cls, bot, module_code, question, answerers):
        # TODO : REMOVE
        # TESTING
        #
        # callback_data is supposed to encode the question_id so that when users click
        # "Answer Question", we will know what question he is answering
        # question_id = KBManager.ask_question(bot.telegram_id, module_code, question)
        #
        # CHECK: Module_code may not exist
        #
        # for answerer in answerers:
        '''
        markup = InlineKeyboardMarkup(inline_keyboard=[
                 [InlineKeyboardButton(text=question, callback_data='notification')]
             ])
        # bot.sender.sendMessage(answerer.telegram_user_id,
        #   "These are the modules that you can subscribe to ...", reply_markup=markup)
        #
        print "Sup"
        '''

# Need another bot?
# bot2 = telepot.Bot(TOKEN)
