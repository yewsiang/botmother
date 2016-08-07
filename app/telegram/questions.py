import telepot
from .commands import State
from .voting import Voting
from telepot.exception import TelegramError
from app.tasks import execute_callback_after_time
from app.accounts import AccountManager
from app.knowledgebase import KBManager, max_questions_per_day
from app.helpers import get_question_by_id, get_weblink_by_question_id
from telepot.namedtuple import ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint


# Classes and functions are arranged in chronological flow.
class AskingQuestions:
    '''
    This class handles the process by which a user asks questions.
    '''
    # /ask - User initiates asking questions by typing "/ask"
    @classmethod
    def ask_command(cls, bot):
        print "<< (Ask 1) /ask Command >>"

        # Retrieve the modules that the User has subscribed to
        subscribed_channels = AccountManager.get_subscribed_channels(bot.telegram_id)

        # User must have subscribed to modules first
        if subscribed_channels == []:
            bot.sender.sendMessage("You have not subscribed to any mods.\n"
                "/<module code> to add a module (E.g /CS1010 adds the module CS1010)")
            return

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
    def process_asking_questions(cls, bot, delegator_bot, msg):
        print "<< (Ask 2) Question has been keyed in >>"

        # Change the state of the User so that we will know he is going to send a module next
        bot.question_asked = msg['text']
        bot.state = State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        bot.sender.sendMessage("Which module would you like to send the question to?")

        # Retrieve the modules that the User has subscribed to
        subscribed_channels = AccountManager.get_subscribed_channels(bot.telegram_id)

        # Automatically list out the modules that the User has subscribed to
        list_of_subscribed_channels = "Your modules subscribed are:\n"
        for channel in subscribed_channels:
            list_of_subscribed_channels += ("/" + str(channel).upper() + " ")
        bot.sender.sendMessage(list_of_subscribed_channels)

    # State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS - When user finished typing his question and is
    # selecting a channel to post the question
    @classmethod
    def process_selecting_channel_after_asking_questions(cls, bot, delegator_bot, command):
        print "<< (Ask 3) /<module code> has been keyed in >>"

        # User may type "/CS1010" or "CS1010", we will support both
        if command[:1] == "/":
            module_code = command[1:]
        else:
            module_code = command

        # Retrieve the modules that the User has subscribed to
        subscribed_channels = AccountManager.get_subscribed_channels(bot.telegram_id)

        # Check if the user is subscribed to the module he is trying to ask questions
        subscribed_to_channel_already = False
        for channel in subscribed_channels:
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
                ". The answers will be sent back to you in 5 mins!")

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

        text_to_send = ("<b>" + module_code.upper() + "</b>\n"
                "Question: " + question)

        # Send the question to everyone subscribed to the module
        for answerer in answerers:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Answer Question",
                        callback_data=('AnswerQuestion_' + str(question_id) + '_None_None'))]
                 ])
            delegator_bot.sendMessage(answerer.telegram_user_id, text_to_send, reply_markup=markup, parse_mode='HTML')

        # Timer function
        # Wait for 15 mins before sending answers to voters
        kwargs_for_time_function = {
            'bot': bot,
            'delegator_bot': delegator_bot,
            'question_id': question_id
        }
        execute_callback_after_time(5 * 60, AnsweringQuestions.send_answers_to_voters, kwargs_for_time_function)


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
        callback_type, question_id, unused, unused = data.split('_')

        can_user_answer_question = KBManager.can_user_answer_question(question_id, bot.telegram_id)
        if can_user_answer_question:
            # Assumption: It is fine to store question_id temporarily in bot since the User
            # MUST click 'Answer Question' every time he wishes to answer a question.
            bot.temp_ans_question_id = question_id
            bot.state = State.ANSWERING_QUESTIONS
            bot.sender.sendMessage("Please type your answer", reply_markup=ForceReply())
        else:
            bot.sender.sendMessage("I'm sorry but we're in the voting process and you have already answered the question. "
                "You can submit answers again after the voting is over :)!")

    # State.ANSWERING_QUESTIONS - User clicks "Answer Question" and enters his answer.
    # After the User typed his answer, this function will send the User a confirmation (Yes/No)
    @classmethod
    def process_confirmation_of_answer(cls, bot, delegator_bot, msg):
        print "<< (Answer 2) User has typed in his answer >>"

        # Store the answer to send before the User's confirmation
        answer_id = KBManager.add_answer_to_question(bot.temp_ans_question_id, bot.telegram_id, msg['text'])

        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Yes",
                        callback_data=('ConfirmAnswer_' + str(answer_id) + '_' + str(bot.temp_ans_question_id) + '_yes')),
                     InlineKeyboardButton(text="No",
                        callback_data=('ConfirmAnswer_' + str(answer_id) + '_' + str(bot.temp_ans_question_id) + '_no'))]
                 ])
        bot.sender.sendMessage("Send your answer?", reply_markup=markup)

    # Callback activated when User presses "Yes" or "No" button in response to the Bot asking
    # if the User wishes to send his answer
    @classmethod
    def callback_confirm_answer(cls, bot, delegator_bot, data, query_id, msg_idf):
        print "<< (Answer 3) 'Yes' or 'No' button has been clicked to confirm answers >>"

        # The User may press multiple times and cause an error
        try:
            callback_type, answer_id, question_id, response = data.split('_')
            msg_idf = (bot.telegram_id, msg_idf)
            if response == 'yes':
                # Send answer to list
                bot.sender.sendMessage("Your answer has been sent! You will be sent other people's answers shortly!")
                delegator_bot.answerCallbackQuery(query_id, "Your answer has been sent!")

                # Confirm the answer to the question. This will make it available to the rest of the Users.
                KBManager.confirm_answer(answer_id)

                # New markup is given a callback_data of sent_None_None_None because the format of callback data is of
                # ABC_DEF_GHI since we will .split('_')
                new_markup = InlineKeyboardMarkup(inline_keyboard=[
                         [InlineKeyboardButton(text="Sent", callback_data="Sent_None_None_None")]
                     ])
                bot.state = State.NORMAL
                delegator_bot.editMessageReplyMarkup(msg_idf, new_markup)

            else:
                new_markup = InlineKeyboardMarkup(inline_keyboard=[
                         [InlineKeyboardButton(text="Cancelled", callback_data="Cancelled_None_None_None")]
                     ])
                bot.state = State.NORMAL
                delegator_bot.editMessageReplyMarkup(msg_idf, new_markup)

        except TelegramError:
            print "Multiple clicks error"

    # (Delayed Function)
    # Sending answers to voters after there are 9 answers / 15mins is up:
    # 1) Clicked on "Answer Question" and triggered the Force Reply
    # 2) Typed their answers and hit "Send"
    # 3) Clicked on "Yes" to confirm their answers
    @classmethod
    def send_answers_to_voters(cls, bot, delegator_bot, question_id):
        print "<< (Answer 4) Answers to be sent to voters >>"

        question = get_question_by_id(question_id)
        answers = KBManager.get_answers_for_qn(question_id)
        voters = KBManager.get_voters_for_qn_answers(question_id)

        # Check that there are answers before sending any messages to the voters
        if len(answers) != 0:
            # Sending the Question and Answers to the voters
            text_to_send = ("<b>" + question.channel.name.upper() + "</b>\n"
                    "Question: " + question.text + "\n"
                    "Answers:\n")
            for idx, answer in enumerate(answers):
                text_to_send += (str(idx + 1) + ". " + answer.text + "\n")

            # Send a inline keyboard button along. This will be modified when the User has successfully voted.
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Vote", callback_data="Vote_" + str(question_id) + "_None_None")]
                 ])

            # Sending to each of the voter
            for voter in voters:
                delegator_bot.sendMessage(voter.telegram_user_id, text_to_send, reply_markup=markup, parse_mode='HTML')

            # Timer function
            # Wait for another 15 mins before sending results to the participants
            kwargs_for_time_function = {
                'bot': bot,
                'delegator_bot': delegator_bot,
                'question_id': question_id,
                'number_of_answers': len(answers)
            }
            execute_callback_after_time(5 * 60, Voting.send_answers_and_link_to_participants, kwargs_for_time_function)

        else:
            # Create link to forum and send message to the person asking the question to tell him that there are no answers
            forum_link = get_weblink_by_question_id(question_id)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Link to Forum', url=forum_link)]
                 ])
            delegator_bot.sendMessage(question.user.telegram_user_id, "There were no answers after 15mins,"
                "we have created a forum post for you and hopefully you will get your answers there :)!", reply_markup=markup)
