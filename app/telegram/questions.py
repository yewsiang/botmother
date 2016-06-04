import telepot
from app.accounts import AccountManager
from app.knowledgebase import KBManager
from .message_blast import MessageBlast
from .commands import State
from telepot.namedtuple import ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint


class AskingQuestions:
    '''
    This class handles the process by which a user asks questions.
    '''
    # State.ASKING_QUESTIONS - When user wants to ask questions for a module
    @classmethod
    def process_asking_questions(cls, bot, delegator_bot, command):
        print "(C) PROCESS ASKING QUESTIONS"
        bot.question_asked = command
        bot.state = State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        bot.sender.sendMessage("Which module would you like to send the question to?")

    # State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS - When user finished typing his question and is
    # selecting a channel to post the question
    @classmethod
    def process_selecting_channel_after_asking_questions(cls, bot, delegator_bot, command):
        print "(C2) PROCESS SELECTING CHANNEL AFTER ASKING QUESTIONS"
        module_code = command[1:]
        #
        # TODO: Check if the user should be allowed to ask questions
        # TODO: Check if the user is subscribed in the module in the first place
        #
        answerers = KBManager.get_answerers(bot.telegram_id, module_code)
        MessageBlast.send_question_to_answerers(bot, delegator_bot, module_code, bot.question_asked, answerers)
        bot.state = State.NORMAL
        bot.sender.sendMessage("Your question has been sent to the people subscribed to " + module_code.upper() +
            ". The answers will be sent back to you in 15 mins!")


class AnsweringQuestions:
    '''
    This class handles the process by which a user answers other users' questions.
    '''
    # State.ANSWERING_QUESTIONS - User clicks "Answer Question" and enters this state.
    # Any incoming message is treated as the answer.
    # Callback activated when User presses "Answer Question" button from other Users' questions.
    @classmethod
    def callback_answer_question(cls, bot, delegator_bot, data, query_id):
        bot.state = State.ANSWERING_QUESTIONS
        bot.sender.sendMessage('Please type your answer', reply_markup=ForceReply())

    # After the User typed his answer, this function will send the User a confirmation (Yes/No)
    @classmethod
    def process_confirmation_of_answer(cls, bot, delegator_bot, command):
        print "(D2) CONFIRMATION OF ANSWERS"
        # Store the answer to send before the User's confirmation
        #
        # TODO: Store the answer to send in DB?
        #
        bot.answer_to_send = command
        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Yes",
                        callback_data=('ConfirmAnswer_' + str(bot.telegram_id) + '_yes')),
                     InlineKeyboardButton(text="No",
                        callback_data=('ConfirmAnswer_' + str(bot.telegram_id) + '_no'))]
                 ])
        #
        # TODO: How to store msg_with_inline_keyboard?
        #
        bot.msg_with_inline_keyboard = bot.sender.sendMessage("Send your answer?", reply_markup=markup)
        pprint(bot.msg_with_inline_keyboard)
        bot.msg_idf = telepot.message_identifier(bot.msg_with_inline_keyboard)
        print bot.msg_idf

    # Callback activated when User presses "Yes" or "No" button in response to the Bot asking
    # if the User wishes to send his answer
    @classmethod
    def callback_confirm_answer(cls, bot, delegator_bot, data, query_id):
        callback_type, id1, response = data.split('_')
        if response == 'yes':
            # Send answer to list
            bot.sender.sendMessage("Your answer has been sent! You will be sent other people's answers shortly!")
            delegator_bot.answerCallbackQuery(query_id, "Your answer has been sent!")
            #
            # KBManager.add_answer_to_question(,bot.telegram_id,)
            #
            # New markup is given a callback_data of sent_NONE_NONE because the format of callback data is of
            # ABC_DEF_GHI since we will .split('_')
            new_markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Sent", callback_data="Sent_None_None")]
                 ])
            bot.state = State.NORMAL
            delegator_bot.editMessageReplyMarkup(bot.msg_idf, new_markup)
            print "Send answer to list"
        else:
            new_markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Cancelled", callback_data="Cancelled_None_None")]
                 ])
            bot.state = State.NORMAL
            bot.sender.sendMessage("Click on Answer Question if you have the answer")
            delegator_bot.editMessageReplyMarkup(bot.msg_idf, new_markup)
