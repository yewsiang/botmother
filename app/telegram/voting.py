from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from app.accounts import AccountManager
from app.knowledgebase import KBManager
from pprint import pprint


class Voting:
    '''
    This class handles
    '''
    # Hello

    # Sending voting results to interested parties after the vote has concluded:
    # 1)
    # 2)
    # Forum link is also sent along so that interested parties can continue the discussion
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
