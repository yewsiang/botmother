from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from app.accounts import AccountManager
from app.knowledgebase import KBManager
from .commands import State
from pprint import pprint


class Voting:
    '''
    This class handles the voting process after the asking and answering of questions are done.
    '''
    # Callback activated when User presses "Vote" button after the question and answers are sent to the User
    @classmethod
    def callback_vote_on_answer(cls, bot, delegator_bot, data, query_id):
        callback_type, question_id, unused = data.split('_')
        bot.state = State.VOTING
        bot.temp_vote_question_id = question_id
        markup = ReplyKeyboardMarkup(keyboard=[
                 [KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3')],
                 [KeyboardButton(text='4'), KeyboardButton(text='5'), KeyboardButton(text='6')],
                 [KeyboardButton(text='7'), KeyboardButton(text='8'), KeyboardButton(text='9')],
                 [KeyboardButton(text='0')]
             ], one_time_keyboard=True)
        bot.sender.sendMessage("Choose the answer that you are confident of. Otherwise, choose '0' :).",
            reply_markup=markup)
        #
        # TODO: This function needs to have a Time element as well (E.g. execute in 30 mins after Qns was sent)
        # Need to place function in appropriate place. This is simply for testing.
        #
        Voting.send_answers_and_link_to_participants(bot, delegator_bot, question_id)

    @classmethod
    def process_voting(cls, bot, delegator_bot, command):
        bot.state = State.NORMAL
        print "---- I have received your vote! ----"
        print command

    # Sending voting results to interested parties after the vote has concluded:
    # 1)
    # 2)
    # Forum link is also sent along so that interested parties can continue the discussion
    @classmethod
    def send_answers_and_link_to_participants(cls, bot, delegator_bot, question_id):
        #
        # TODO
        #
        # After the voting has finalized, we will send the answers, votes and link to
        # those who participated
        #
        markup = InlineKeyboardMarkup(inline_keyboard=[
                 [dict(text='Link to Forum', url='https://core.telegram.org/')]
             ])
        print "Wala Wala"
        # bot.sender.sendMessage(reply_markup=markup)
