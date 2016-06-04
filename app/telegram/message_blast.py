from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from app.accounts import AccountManager
from app.knowledgebase import KBManager
from pprint import pprint


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
    def send_question_to_answerers(cls, bot, delegator_bot, module_code, question, answerers):
        # callback_data is supposed to encode the question_id so that when users click
        # "Answer Question", we will know what question he is answering
        question_id = KBManager.ask_question(bot.telegram_id, module_code, question)
        answerers = KBManager.get_answerers(bot.telegram_id, module_code)
        #
        # CHECK: Module_code may not exist
        #
        print "Question_id: " + str(question_id)
        for answerer in answerers:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Answer Question",
                        callback_data=('AnswerQuestion_' + str(question_id) + '_blank'))]
                 ])
            print answerer.telegram_user_id
            delegator_bot.sendMessage(answerer.telegram_user_id, question, reply_markup=markup)

    @classmethod
    def send_answers_to_voters(cls, bot, delegator_bot, answers_text, voters):
        #
        # for voter in voters:
        #     delegator_bot.sendMessage(voter.telegram_user_id, answers_text)
        #
        print "Hi"

    @classmethod
    def send_answers_and_link_to_participants(cls, bot, delegator_bot, participants):
        #
        # TODO
        #
        # After the voting has finalized, we will send the answers, votes and link to
        # those who participated
        #
        markup = InlineKeyboardMarkup(inline_keyboard=[
                 [dict(text='Link to Forum', url='https://core.telegram.org/')]
             ])
        # bot.sender.sendMessage(reply_markup=markup)
