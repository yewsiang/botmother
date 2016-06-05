from .commands import State
from .questions import AskingQuestions, AnsweringQuestions


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
        callback_type, param1, param2 = data.split('_')
        print callback_type

        # Callback queries for Answering of questions
        if callback_type == 'AnswerQuestion':
            AnsweringQuestions.callback_answer_question(bot, delegator_bot, data, query_id)
        elif callback_type == 'ConfirmAnswer':
            AnsweringQuestions.callback_confirm_answer(bot, delegator_bot, data, query_id)
        elif callback_type == 'Sent':
            delegator_bot.answerCallbackQuery(query_id, text='Your answer has been sent!')
        elif callback_type == 'Cancelled':
            delegator_bot.answerCallbackQuery(query_id, text='Your answer was cancelled!')

        elif data == 'question_answered':
            CallbackQueries.question_answered(bot, delegator_bot, data, query_id)
