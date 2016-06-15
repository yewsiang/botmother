import telepot
from app.helpers import get_question_by_id
from app.knowledgebase import KBManager, max_questions_per_day
from .commands import State
from telepot.namedtuple import ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint


class AskingQuestions:
    '''
    This class handles the process by which a user asks questions.
    '''
    # /ask - User initiates asking questions by typing "/ask"
    @classmethod
    def ask_command(cls, bot):
        print "<< (Ask 1) /ask Command >>"

        # User wants to ask questions
        # Check if the User has asked too many questions for the day
        user_can_ask_questions = KBManager.can_user_ask_question(bot.telegram_id)
        if user_can_ask_questions:
            bot.state = State.ASKING_QUESTIONS
            bot.sender.sendMessage("Tell us what question you have :). After which, you can choose a module to send the question to!")
        else:
            bot.sender.sendMessage("I'm sorry but you can only ask " + str(max_questions_per_day) +
                " questions per day. Please continue again tomorrow :)!")

    # State.ASKING_QUESTIONS - When User types in his question and it is sent to this function
    @classmethod
    def process_asking_questions(cls, bot, delegator_bot, command):
        print "<< (Ask 2) Question has been keyed in >>"

        # Change the state of the User so that we will know he is going to send a module next
        bot.question_asked = command
        bot.state = State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        bot.sender.sendMessage("Which module would you like to send the question to?")

    # State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS - When user finished typing his question and is
    # selecting a channel to post the question
    @classmethod
    def process_selecting_channel_after_asking_questions(cls, bot, delegator_bot, command):
        print "<< (Ask 3) /<module code> has been keyed in >>"

        # User may type "/MOM1000" or "MOM1000", we will support both
        if command[:1] == "/":
            module_code = command[1:]
        else:
            module_code = command

        # Check if the user is subscribed to the module he is trying to ask questions
        subscribed_to_channel_already = False
        for channel in bot.subscribed_channels:
            if str(channel) == module_code:
                subscribed_to_channel_already = True

        # Send the question only after the User has subscribed to that module
        if not subscribed_to_channel_already:
            bot.state = State.NORMAL
            bot.sender.sendMessage("I'm sorry but you will need to be subscribed to /" + module_code.upper() +
                " before you are allowed to post a question for that module")
        else:
            # Get everyone in the channel in order to send them the question
            answerers = KBManager.get_answerers(bot.telegram_id, module_code)
            AskingQuestions.send_question_to_answerers(bot, delegator_bot, module_code, bot.question_asked, answerers)
            # Back to NORMAL state after question ahs been sent
            bot.state = State.NORMAL
            bot.sender.sendMessage("Your question has been sent to the people subscribed to " + module_code.upper() +
                ". The answers will be sent back to you in 15 mins!")

    # Sending questions to answerers after they have finished:
    # 1) Typing their question,
    # 2) Selecting a channel
    @classmethod
    def send_question_to_answerers(cls, bot, delegator_bot, module_code, question, answerers):
        print "<< (Ask 4) Question will now be sent to answerers >>"

        # callback_data is supposed to encode the question_id so that when users click
        # "Answer Question", we will know what question he is answering
        question_id = KBManager.ask_question(bot.telegram_id, module_code, question)
        answerers = KBManager.get_answerers(bot.telegram_id, module_code)

        # Send the question to everyone subscribed to the module
        for answerer in answerers:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Answer Question",
                        callback_data=('AnswerQuestion_' + str(question_id) + '_None'))]
                 ])
            delegator_bot.sendMessage(answerer.telegram_user_id, question, reply_markup=markup)


class AnsweringQuestions:
    '''
    This class handles the process by which a user answers other users' questions.
    '''
    # State.ANSWERING_QUESTIONS - User clicks "Answer Question" and enters this state.
    # Any incoming message is treated as the answer.
    # Callback activated when User presses "Answer Question" button from other Users' questions.
    @classmethod
    def callback_answer_question(cls, bot, delegator_bot, data, query_id):
        print "<< (Answer 1) 'Answer Question' button has been clicked >>"

        # Checks if the User is trying to answer the question more than once while it is still under voting.
        # We do not want to allow the User to spam the voting process with his answers.
        callback_type, question_id, unused = data.split('_')
        #
        # TODO: CHECK FOR CORRECTNESS
        #
        can_user_answer_question = KBManager.can_user_answer_question(question_id, bot.telegram_id)
        if can_user_answer_question:
            bot.temp_answer_question_id = question_id
            bot.state = State.ANSWERING_QUESTIONS
            bot.sender.sendMessage("Please type your answer", reply_markup=ForceReply())
        else:
            bot.sender.sendMessage("I'm sorry but we're in the voting process and you have already answered the question. "
                "You can submit answers again after the voting is over :)!")

    # State.ANSWERING_QUESTIONS - User clicks "Answer Question" and enters his answer.
    # After the User typed his answer, this function will send the User a confirmation (Yes/No)
    @classmethod
    def process_confirmation_of_answer(cls, bot, delegator_bot, command):
        print "<< (Answer 2) User has typed in his answer >>"

        # Store the answer to send before the User's confirmation
        #
        # TODO: Store the answer to send in DB?
        #
        bot.answer_to_send = command

        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Yes",
                        callback_data=('ConfirmAnswer_' + str(bot.temp_answer_question_id) + '_yes')),
                     InlineKeyboardButton(text="No",
                        callback_data=('ConfirmAnswer_' + str(bot.temp_answer_question_id) + '_no'))]
                 ])
        #
        # TODO: How to store msg_with_inline_keyboard?
        #
        bot.msg_with_inline_keyboard = bot.sender.sendMessage("Send your answer?", reply_markup=markup)
        pprint(bot.msg_with_inline_keyboard)
        '''
        bot.msg_idf = telepot.message_identifier(bot.msg_with_inline_keyboard)
        print bot.msg_idf
        '''

    # Callback activated when User presses "Yes" or "No" button in response to the Bot asking
    # if the User wishes to send his answer
    @classmethod
    def callback_confirm_answer(cls, bot, delegator_bot, data, query_id):
        print "<< (Answer 3) 'Yes' or 'No' button has been clicked to confirm answers >>"

        callback_type, question_id, response = data.split('_')
        if response == 'yes':
            # Send answer to list
            bot.sender.sendMessage("Your answer has been sent! You will be sent other people's answers shortly!")
            delegator_bot.answerCallbackQuery(query_id, "Your answer has been sent!")

            # Add the answer to the question
            #
            # TODO: Need to get the answer_to_send from the db later on
            #
            KBManager.add_answer_to_question(question_id, bot.telegram_id, bot.answer_to_send)

            # New markup is given a callback_data of sent_NONE_NONE because the format of callback data is of
            # ABC_DEF_GHI since we will .split('_')
            new_markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Sent", callback_data="Sent_None_None")]
                 ])
            bot.state = State.NORMAL
            delegator_bot.editMessageReplyMarkup(bot.msg_idf, new_markup)

            #
            # TODO: This function needs to have a Time element (E.g. execute in 15 mins)
            #
            AnsweringQuestions.send_answers_to_voters(bot, delegator_bot, question_id)

        else:
            new_markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Cancelled", callback_data="Cancelled_None_None")]
                 ])
            bot.state = State.NORMAL
            delegator_bot.editMessageReplyMarkup(bot.msg_idf, new_markup)

    # Sending answers to voters after answerers have:
    # 1) Clicked on "Answer Question" and triggered the Force Reply
    # 2) Typed their answers and hit "Send"
    # 3) Clicked on "Yes" to confirm their answers
    @classmethod
    def send_answers_to_voters(cls, bot, delegator_bot, question_id):
        print "<< (Answer 4) Answers to be sent to voters >>"

        question = get_question_by_id(question_id)
        answers = KBManager.get_answers_for_qn(question_id)
        voters = KBManager.get_voters_for_qn_answers(question_id)

        #
        # TODO: Check for the situation where there are no answers
        #
        # Sending the Question and Answers to the voters
        text_to_send = "Question: " + question.text + "\n"
        text_to_send += "Answers:\n"
        for id, answer in enumerate(answers):
            text_to_send += (str(id + 1) + ". " + answer.text + "\n")
        text_to_send += "\nChoose the answer that you are confident of. Otherwise, choose '0' :)."

        # Send a inline keyboard button along
        markup = InlineKeyboardMarkup(inline_keyboard=[
                 [InlineKeyboardButton(text="Vote", callback_data="Vote_" + str(question_id) + "_None")]
             ])

        print "---- Text_to_send is ----"
        print text_to_send

        # Sending to each of the voter
        for voter in voters:
            delegator_bot.sendMessage(voter.telegram_user_id, text_to_send, reply_markup=markup)
        print "We are sending the answers to the voters!"
