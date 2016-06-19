from .commands import State
from .questions import AnsweringQuestions
from .voting import Voting


class CallbackQueries:
    '''
    This class handles the callback functions.
    The "data" variable will encode the information.
    The "delegator_bot" is to allow notifications on the top of the screen.
    '''
    @classmethod
    def on_answer(cls, bot, delegator_bot, data, query_id, msg_idf=None):
        # All callback queries will pass through this function and be allocated to
        # a suitable function to handle it based on information in "data"
        callback_type, param1, param2, param3 = data.split('_')
        print callback_type

        # Callback queries for Answering of questions
        if callback_type == 'AnswerQuestion':
            # When "Answer Question" button has been clicked after User submits question
            AnsweringQuestions.callback_answer_question(bot, delegator_bot, data, query_id)
        elif callback_type == 'ConfirmAnswer':
            # When "Yes" or "No" button has been clicked after User submits answer
            AnsweringQuestions.callback_confirm_answer(bot, delegator_bot, data, query_id, msg_idf)
        elif callback_type == 'Sent':
            # User clicks on "Sent" button even after he has sent his answer
            delegator_bot.answerCallbackQuery(query_id, text='Your answer has already been sent!')
        elif callback_type == 'Cancelled':
            # User clicks on "Cancelled" button even after he has cancelled his answer
            delegator_bot.answerCallbackQuery(query_id, text='Your answer was already cancelled!')

        # Callback queries for Voting
        elif callback_type == 'Vote':
            # When answers have been submitted and sent for voting
            # User clicks "Vote" button
            Voting.callback_vote_on_answer(bot, delegator_bot, data, query_id, msg_idf)
        elif callback_type == 'Voted':
            # User clicks on "Voted" button even after he has Voted
            delegator_bot.answerCallbackQuery(query_id, text='You have voted already!')
