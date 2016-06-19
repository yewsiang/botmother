from test_base import BaseTestCase
from app.helpers import get_answer_by_id
from app.accounts import TelegramAccountManager, AccountManager, User
from app.knowledgebase import Channel, Question
from app import db
from sqlalchemy.exc import IntegrityError
from app.knowledgebase import KBManager

from app.telegram import Command, State, CallbackQueries


# Create a fake bot that stores the messages sent to the user in a variable
# to allow us to test the messages sent to the user
# telepot uses self.bot.sender.sendMessage(msg) to send messages to user

# Compare 2 lists of messages and make sure they are the same
def compare_two_lists_sequentially(self, incoming_messages, expected_messages):
    if (len(incoming_messages) != len(expected_messages)):
        return False
    are_identical_messages = True
    for i, incoming_message in enumerate(incoming_messages):
        if (incoming_message != expected_messages[i]):
            are_identical_messages = False
    return are_identical_messages


# These fake bots support spoofing of bot.sender.sendMessage().
# This allows testing of the exact messages sent to the User.
# (Should have a better way)
class FakeBot:
    def __init__(self, telegram_id, state):
        self.sender = SecondFakeBot()
        self.telegram_id = telegram_id
        self.state = state
        # hack to support bot.msg_idf usage
        self.msg_idf = 0

    def get_messages(self):
        return self.sender.messages


class SecondFakeBot:
    def __init__(self):
        self.messages = []

    # reply_markup to prevent error when parameter reply_markup is passed in
    def sendMessage(self, msg, reply_markup=None):
        self.messages.append(msg)


class FakeDelegatorBot:
    def __init__(self):
        self.messages = []
        self.send_message_list = []
        self.answer_callback_query_list = []
        self.edit_message_reply_list = []

    def sendMessage(self, telegram_id, question, reply_markup=None):
        msg = [telegram_id, question, reply_markup]
        self.messages.append(msg)
        self.send_message_list.append(msg)

    # not supposed to have markup as argument but put here so that it is easier to parse in the tests.
    # this is because of map(lambda msg: msg[:-1]) which seeks to remove the markup of each message
    def answerCallbackQuery(self, query_id, msg, markup=None):
        msg = [query_id, msg, markup]
        self.messages.append(msg)
        self.answer_callback_query_list.append(msg)

    def editMessageReplyMarkup(self, msg_id, markup=None):
        msg = [msg_id, markup]
        self.messages.append(msg)
        self.edit_message_reply_list.append(msg)

    def get_messages(self):
        return self.messages


class TelegramTests(BaseTestCase):
    # Testing the Fake bots
    def test_fakebot_send_message(self):
        '''
        Tests that users commands are sent properly
        '''
        bot = FakeBot(123, State.NORMAL)
        bot.sender.sendMessage("Hello")
        bot.sender.sendMessage("world")
        expected_messages = ["Hello", "world"]
        assert bot.get_messages() == expected_messages

    def test_fakedelegatorbot_send(self):
        '''
        Tests that delegator bot is able to send messages, answer callback queries, and edit message replies
        '''
        delegator_bot = FakeDelegatorBot()
        delegator_bot.sendMessage(1, "How are you?", None)
        delegator_bot.sendMessage(2, "Wala wala papapya", ["Some random complicated markup stuff", 1])
        expected_messages1 = [[1, "How are you?", None],
            [2, "Wala wala papapya", ["Some random complicated markup stuff", 1]]]

        delegator_bot.answerCallbackQuery(1, "Some message")
        delegator_bot.answerCallbackQuery(2, "Some more message")
        expected_messages2 = [[1, "Some message", None],
            [2, "Some more message", None]]

        delegator_bot.editMessageReplyMarkup(1, ["Some stuff", 1])
        delegator_bot.editMessageReplyMarkup(2, ["Some more stuff", 2])
        expected_messages3 = [[1, ["Some stuff", 1]],
            [2, ["Some more stuff", 2]]]

        assert (delegator_bot.send_message_list == expected_messages1)
        assert (delegator_bot.answer_callback_query_list == expected_messages2)
        assert (delegator_bot.edit_message_reply_list == expected_messages3)

    #
    # Modules class testing
    #
    # Testing /me command
    def test_me_command_with_modules(self):
        '''
        /me command should retrieve the modules that a User has subscribed
        '''
        bot = FakeBot(123, State.NORMAL)
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        cs1231 = Channel(name='cs1231')
        u1.channels.append(cs2100)
        u1.channels.append(cs1231)

        # Call the function in the Telegram module
        # TODO: Modules.me_command(fakeBot)
        Command.process_commands(bot, bot, '/me')

        print bot.get_messages()
        expected_messages = ["Your modules subscribed are CS2100 CS1231 "]
        assert bot.get_messages() == expected_messages

    def test_me_command_without_modules(self):
        '''
        /me command should inform user that he doesn't have any modules
        '''
        bot = FakeBot(123, State.NORMAL)
        u1 = self.create_user(123, 0)

        # Call the function in the Telegram module
        # Modules.me_command(fakeBot)
        Command.process_commands(bot, bot, '/me')

        print bot.get_messages()
        expected_messages = ["You have not subscribed to any mods.\n"
            "/<module code> to add a module (E.g /PAP1000 adds the module PAP1000)"]
        assert bot.get_messages() == expected_messages

    # Testing /modules command
    def test_modules_command(self):
        '''
        /modules command should retrieve all the available modules
        '''
        bot = FakeBot(123, State.NORMAL)
        u1 = self.create_user(123, 0)

        db.session.add(Channel(name='pap1000'))
        db.session.add(Channel(name='bro1000'))
        db.session.add(Channel(name='sis1000'))

        # Call the function in the Telegram module
        # Modules.me_command(fakeBot)
        Command.process_commands(bot, bot, '/modules')
        expected_messages = ["Modules available:  /PAP1000  /BRO1000  /SIS1000  "]
        assert bot.get_messages() == expected_messages

    #
    # Questions class testing
    #
    def test_user_asking_question(self):
        '''
        Test one full cycle of the question asking process with 1 asker and 2 answerers. 1 extra.
        1) Asker asks question
        2) Question gets sent to the 2 answerers
        Check if the bots & delegator_bots sent the correct messages
        '''
        # Initialize the Users and a bot and delegator_bot for the asker
        bot = FakeBot(1, State.NORMAL)
        delegator_bot = FakeDelegatorBot()
        u1 = self.create_user(1, 0)
        u2 = self.create_user(2, 0)
        u3 = self.create_user(3, 0)
        u4 = self.create_user(4, 0)

        # Create a channel that ALL but ONE (u4) will join (to test if the question gets sent wrongly to u4)
        db.session.add(Channel(name='pap1000'))
        AccountManager.add_channel(u1.telegram_user_id, 'pap1000')
        AccountManager.add_channel(u2.telegram_user_id, 'pap1000')
        AccountManager.add_channel(u3.telegram_user_id, 'pap1000')

        # User1 types /ask and is now in State.ASKING_QUESTIONS
        Command.process_commands(bot, delegator_bot, '/ask')
        first_msg = bot.get_messages()
        expected_message1 = ["Tell us what question you have :). After which, you can choose a module to send the question to!"]
        assert first_msg == expected_message1

        # User1 asks a question and is now in State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        # We have to ask him what module he would like to send it to
        Command.process_commands(bot, delegator_bot, 'Question by User 1')
        second_msg = bot.get_messages()
        expected_message2 = ["Which module would you like to send the question to?"]
        assert second_msg[1:] == expected_message2

        # User1 now types in the /<module code> of the module that he wants to send it to
        Command.process_commands(bot, delegator_bot, '/pap1000')
        third_msg = bot.get_messages()
        expected_message3 = ["Your question has been sent to the people subscribed to PAP1000. The answers will be sent back to you in 15 mins!"]

        print "------------ bot -------------"
        print third_msg
        print "------- delegator bot --------"
        # AskingQuestions use delegator_bot to send messages to everyone
        delegator_bot_messages = delegator_bot.get_messages()
        # Remove the keyboard markup of each of the message
        delegator_bot_messages_without_markup = map(lambda msg: msg[:-1], delegator_bot_messages)
        print delegator_bot_messages_without_markup
        expected_delegatorbot_message = [[2, 'Question by User 1'],
            [3, 'Question by User 1']]

        assert ((third_msg[2:] == expected_message3) and
            (delegator_bot_messages_without_markup == expected_delegatorbot_message))
    def test_get_correct_web_link(self):
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        # answer question AND change the state to non 0 - should
        # mean that we can't answer
        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')
        KBManager.change_question_state(question_id, 1)

        web_link = KBManager.get_web_link_for_question(question_id)
        print "web link: " + str(web_link)
        assert KBManager.get_web_link_for_question(question_id) == "/knowledgebase/" + str(question_id)

    def test_user_answering_question(self):
        '''
        (Continued from test_user_asking_question)
        Test a few Users answering a question that has been asked. (1 asker, 2 answers, 1 extra).
        After a User asked a question:
        1) 2 Users reply to the question
        Check if the bots & delegator_bots sent the correct messages
        '''

        # (Initialization will be similar to test_user_asking_question)
        # Initialize the Users and a bot and delegator_bot for the asker
        bot = FakeBot(1, State.NORMAL)
        delegator_bot = FakeDelegatorBot()
        u1 = self.create_user(1, 0)
        u2 = self.create_user(2, 0)
        u3 = self.create_user(3, 0)
        u4 = self.create_user(4, 0)
        # Create a channel that ALL but ONE (u4) will join (to test if the question gets sent wrongly to u4)
        db.session.add(Channel(name='pap1000'))
        AccountManager.add_channel(u1.telegram_user_id, 'pap1000')
        AccountManager.add_channel(u2.telegram_user_id, 'pap1000')
        AccountManager.add_channel(u3.telegram_user_id, 'pap1000')

        # User1 types /ask and is now in State.ASKING_QUESTIONS
        Command.process_commands(bot, delegator_bot, '/ask')
        # User1 asks a question and is now in State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        # We have to ask him what module he would like to send it to
        Command.process_commands(bot, delegator_bot, 'Question by User 1')
        # User1 now types in the /<module code> of the module that he wants to send it to
        Command.process_commands(bot, delegator_bot, '/pap1000')

        print "----"
        delegator_bot_messages_without_markup = map(lambda msg: msg[:-1], delegator_bot.get_messages())
        print delegator_bot_messages_without_markup
        print "----"

        # User2 & User3 answers the question by clicking on the "Answer Question" button.
        # This triggers a callback query which is handled by the CallbackQueries class.
        # Simulate User2 answering the question
        # Current bot has telegram_id of 1, change to 2 and send a message to simulate 2 sending a message
        bot.telegram_id = 2
        bot.answer_to_send = 'Question by User 1'
        # The below simulates a click on the button.
        # (Have to do this because we can't import AnsweringQuestions class)
        CallbackQueries.on_answer(bot, delegator_bot, "AnswerQuestion_1_None_None", 2)
        Command.process_commands(bot, delegator_bot, 'Answer by User 2')
        # Simulate User2 clicking on the "Yes" button to confirm his answer
        CallbackQueries.on_answer(bot, delegator_bot, "ConfirmAnswer_1_1_yes", 4)

        print get_answer_by_id(1)

        print "-----"
        print bot.get_messages()[3:]
        delegator_bot_messages_without_markup = map(lambda msg: msg[:-1], delegator_bot.get_messages())
        print delegator_bot_messages_without_markup[2:]

        # CallbackQueries.on_answer(bot, delegator_bot, "AnswerQuestion_1_None", 3)

        assert False

    #
    # Voting class testing
    #


class KBManagerTests(BaseTestCase):
    def test_can_answer_qn_because_have_not_answered(self):
        '''
        Should be able to answer because we haven't answered before
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        # answer question AND change the state to non 0 - should
        # mean that we can't answer
        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')
        KBManager.change_question_state(question_id, 1)

        assert KBManager.can_user_answer_question(question_id, u1.telegram_user_id) is True

    def test_can_answer_qn_because_not_voting(self):
        '''
        Should be able to answer because it's not voting time
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        # answer question AND change the state to non 0 - should
        # mean that we can't answer
        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')
        KBManager.add_answer_to_question(question_id, u1.telegram_user_id, "42")
        KBManager.change_question_state(question_id, 0)

        assert KBManager.can_user_answer_question(question_id, u1.telegram_user_id) is True

    def test_can_answer_qn_actually_cannot_because_voting(self):
        '''
        Should not be able to answer question because we
        answered and it's voting time!
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        # answer question AND change the state to non 0 - should
        # mean that we can't answer
        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')
        KBManager.add_answer_to_question(question_id, u1.telegram_user_id, "42")
        KBManager.change_question_state(question_id, 1)

        assert KBManager.can_user_answer_question(question_id, u1.telegram_user_id) is False

    def test_change_question_state(self):
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        qn = db.session.query(Question).get(question_id)
        assert qn.state == 0

        KBManager.change_question_state(question_id, 3)
        assert qn.state == 3


    def test_can_user_ask_question_pass(self):
        '''
        Ask only a few questions and see if we can ask another one
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        for i in xrange(20):
            KBManager.ask_question(123, 'cs2100', 'what is life?')

        assert KBManager.can_user_ask_question(u1.telegram_user_id) is True

    def test_can_user_ask_question(self):
        '''
        Ask just above the limit of number of questions and see if we can ask another one
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        for i in xrange(21):
            KBManager.ask_question(123, 'cs2100', 'what is life?')

        assert KBManager.can_user_ask_question(u1.telegram_user_id) is False

    def test_get_voters_for_question_answers(self):
        '''
        Returns everyone who has not answered the questions and is in this
        channel and is NOT the asker of the qn
        u1 is the question asker and should not be returned
        u2 is the one who will answer and should not be returned
        u3 should be returned since he's not in the answerer list
        u4 should not be returned since he's not in the same channe;
        '''
        u1 = self.create_user(123, 0)
        cs2100 = Channel(name='cs2100')
        u1.channels.append(cs2100)

        u2 = self.create_user(124, 0)
        u2.channels.append(cs2100)

        u3 = self.create_user(125, 0)
        u3.channels.append(cs2100)

        u4 = self.create_user(126, 0)
        u4.channels.append(Channel(name='cs2020'))

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()

        answers = ["42", "36", "29", "55"]
        answer_ids = []

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        # add all the answers
        for i in answers:
            answer_ids.append(KBManager.add_answer_to_question(question_id, u2.telegram_user_id, i))

        # confirmation of the answers
        for answer_id in answer_ids:
            KBManager.confirm_answer(answer_id)

        voters = KBManager.get_voters_for_qn_answers(question_id)

        print "voters: " + str(voters)
        print "u3: " + str(u3)

        assert voters == [u3]

    def test_get_answers_for_question(self):
        '''
        Tests that we get the correct list of answers for a question.
        All answers have been confirmed.
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        u2 = self.create_user(124, 0)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        answers = ["42", "36", "29", "55"]
        answer_ids = []

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        # add all the answers
        for i in answers:
            answer_ids.append(KBManager.add_answer_to_question(question_id, u1.telegram_user_id, i))

        # confirmation of all the answers
        for answer_id in answer_ids:
            KBManager.confirm_answer(answer_id)

        # gets all the answer texts
        found_answers = map(lambda x: x.text, KBManager.get_answers_for_qn(question_id))
        print found_answers

        # check that their unordered versions are the same
        assert set(answers) == set(found_answers)
        assert False

    def test_get_answers_for_question_with_unconfirmed_answers(self):
        '''
        Tests that we get the correct list of answers for a question.
        2/4 answer have been confirmed.
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        u2 = self.create_user(124, 0)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        answers = ["42", "36", "29", "55"]
        answer_ids = []

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        # add all the answers
        for i in answers:
            answer_ids.append(KBManager.add_answer_to_question(question_id, u1.telegram_user_id, i))

        # confirmation of the first 2 answers
        for answer_id in answer_ids:
            if (answer_id == 1 or answer_id == 2):
                KBManager.confirm_answer(answer_id)

        # gets all the answer texts
        found_answers = map(lambda x: x.text, KBManager.get_answers_for_qn(question_id))
        expected_answers = ["42", "36"]

        # check that their unordered versions are the same
        assert set(expected_answers) == set(found_answers)

    def test_add_valid_vote_to_valid_answer(self):
        '''
        Tests simple case of adding a valid vote to a valid answer
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        u2 = self.create_user(124, 0)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')
        answer_id = KBManager.add_answer_to_question(question_id, u1.telegram_user_id, "42")

        assert KBManager.add_vote_to_answer(answer_id, u2.telegram_user_id, 1) is True

    def test_add_valid_answer_to_valid_question(self):
        '''
        This tests adding a valid answer to an existing question
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        assert KBManager.add_answer_to_question(question_id,
                                                u1.telegram_user_id,
                                                "42") == 1

    def test_add_too_long_answer_to_valid_question(self):
        '''
        This tests adding an answer that is 5001 chars, > 5000 char limit in DB
        to a valid question, expects ValueError
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # long answer - too long
        answer = "".join([str(i) for i in range(10) for _ in xrange(500)]) + 'a'

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        self.assertRaises(ValueError, KBManager.add_answer_to_question,
                          question_id, u1.telegram_user_id, answer)

    def test_add_blank_answer_to_valid_question(self):
        '''
        This tests adding an invalid (blank) answer to a valid question,
        expects ValueError
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # non-answer
        answer = ""

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        self.assertRaises(ValueError, KBManager.add_answer_to_question,
                          question_id, u1.telegram_user_id, answer)

    def test_add_valid_answer_to_invalid_question(self):
        '''
        This tests trying to  add a valid answer to a question
        that does not exist, expects ValueError
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # valid answer
        answer = "42"

        # does not exist
        question_id = 7000

        self.assertRaises(ValueError, KBManager.add_answer_to_question,
                          question_id, u1.telegram_user_id, answer)

    def test_add_valid_answer_to_valid_question_with_invalid_user(self):
        '''
        This test tries to add a valid answer to a valid question but
        the answerer id does not exist. Expects ValueError
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # valid answer
        answer = "42"

        # does not exist
        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        # user telegram id that does not exist
        self.assertRaises(ValueError, KBManager.add_answer_to_question,
                          question_id, 500, answer)

    def test_ask_valid_question(self):
        '''
        This tests that when a valid question is asked, the correct question
        id is returned
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # ensure that we get the right question id returned
        assert KBManager.ask_question(123, 'cs2100', "hi") == 1

    def test_ask_blank_question(self):
        '''
        This test asks a question that is just an empty string,
        expects a ValueError since non-questions are not allowed
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # ensure that we get the right question id returned
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "")

    def test_ask_question_from_non_user(self):
        '''
        This test asks a question from a user id that does not exist and
        expects a ValueError
        '''
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "a")

    def test_ask_question_for_nonexistent_channel(self):
        '''
        This tests asks a question in a channel that does not exist,
        expects ValueError
        '''
        self.create_user(123, 0)
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "a")

    def test_ask_too_long_question(self):
        '''
        This test asks a question that is too long for the current DB limit
        of VARCHAR(5000) - asks a 5001 char long qn. Expects a ValueError
        '''
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # create a looong question - 5001 characters
        question = "".join([str(i) for i in range(10) for _ in xrange(500)]) + "a"

        print len(question)

        # ensure that we get the right question id returned
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', question)

    def test_get_answerers(self):
        '''
        This test creates 3 users
            u1 -> question asker in cs2100
            u2 -> a subscriber in cs2100
            u3 -> a subscriber in another channel
        KBManager.get_answerers should only return u2
        '''
        u1 = self.create_user(123, 0)
        u2 = self.create_user(124, 0)
        u3 = self.create_user(125, 0)

        # bind first 2 users to first channel
        new_channel = Channel(name='cs2100')
        u1.channels.append(new_channel)
        u2.channels.append(new_channel)

        # bind third user to different channel
        u3.channels.append(Channel(name='cs2020'))

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # we want this to return only u2 - as the only other
        # subscriber to cs2100
        answerers = KBManager.get_answerers(123, 'cs2100')
        assert answerers == [u2]

    def test_get_answerers_for_nonexistent_user(self):
        '''
        This tests tries to get answerers for a
        non_existent telegram_user_id
        '''
        u1 = self.create_user(123, 0)
        u2 = self.create_user(124, 0)
        u3 = self.create_user(125, 0)

        # bind first 2 users to first channel
        new_channel = Channel(name='cs2100')
        u1.channels.append(new_channel)
        u2.channels.append(new_channel)

        # bind third user to different channel
        u3.channels.append(Channel(name='cs2020'))

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # trying to get answerers that don't include the telegram user 10005
        answerers = KBManager.get_answerers(10005, 'cs2100')
        assert answerers == [u1, u2]

    def test_get_answerers_for_nonexistent_channel(self):
        '''
        This tests tries to get answerers for a
        non_existent telegram_user_id
        '''
        u1 = self.create_user(123, 0)
        u2 = self.create_user(124, 0)
        u3 = self.create_user(125, 0)

        # bind first 2 users to first channel
        new_channel = Channel(name='cs2100')
        u1.channels.append(new_channel)
        u2.channels.append(new_channel)

        # bind third user to different channel
        u3.channels.append(Channel(name='cs2020'))

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

        # trying to get answerers that don't include the telegram user 10005
        self.assertRaises(ValueError, KBManager.get_answerers, 123, 'cs5050')


class UserTests(BaseTestCase):
    def test_unique_telegram_user_id(self):
        '''
        Tests that we can't create two users with the same telegram
        user id
        '''
        # Create 123 user
        self.create_user()

        # user does not exist
        new_user_2 = User(123, 4)
        # Add to database
        db.session.add(new_user_2)

        # Commit changes - SHOULD FAIL because of unique telegram id constraint
        self.assertRaises(IntegrityError, db.session.commit)

    def test_get_channels_none(self):
        '''
        Simple test that getting channels for a user without
        channels returns an empty list
        '''

        new_user = self.create_user()

        assert new_user.channels == []

    def test_get_channels_with_some(self):

        new_user = self.create_user()

        # create a new channel
        new_channel = Channel(name='cs2100')
        new_user.channels.append(new_channel)

        db.session.add(new_user)
        db.session.commit()

        new_user = db.session.query(User).get(new_user.id)
        # Check that the channels in the db -> the new channel we just created
        assert new_user.channels == [new_channel]


class TelegramAccountManagerTests(BaseTestCase):
    def test_create_if_not_exists(self):
        '''
        Tests that the create account method works properly
        '''
        res1 = TelegramAccountManager.create_account_if_does_not_exist(123)
        res2 = TelegramAccountManager.create_account_if_does_not_exist(123)
        assert res1 is False
        assert res2 is True


class AccountManagerTests(BaseTestCase):
    def test_get_channels(self):
        '''
        Tests that we can retrieve a user's channels from the db
        '''
        new_user = self.create_user()

        # create a new channel
        new_channel = Channel(name='cs2100')
        new_user.channels.append(new_channel)

        db.session.add(new_user)
        db.session.commit()

        channels = AccountManager.get_subscribed_channels(123)
        # Check that the channels in the db -> the new channel we just created
        assert channels == [new_channel]

    def test_get_channels_without_user(self):
        '''
        Tests that this method returns None for a non-existent user
        '''
        assert AccountManager.get_subscribed_channels(000) is None

    def test_get_channels_with_no_channels(self):
        '''
        Tests that for a user with no channels, we return []
        '''
        self.create_user()
        assert AccountManager.get_subscribed_channels(123) == []

    def test_add_channel_to_non_user(self):
        '''
        Tests that we can't add a channel to a non-existent user
        '''
        assert AccountManager.add_channel(124, 'cs2100') is False

    def test_add_non_channel_to_user(self):
        '''
        Tests that we can't add a non-existent channel to a user
        '''
        new_user = self.create_user()
        assert AccountManager.add_channel(
            new_user.telegram_user_id, 'cs2100') is False

    def test_add_channel_to_user(self):
        '''
        Tests that we can retrieve a user's channels from the db
        '''
        new_user = self.create_user()

        # create a new channel
        new_channel = Channel(name='cs2100')
        db.session.add(new_channel)
        db.session.commit()

        assert AccountManager.add_channel(
            new_user.telegram_user_id, new_channel.name) is True
        assert AccountManager.get_subscribed_channels(
            new_user.telegram_user_id) == [new_channel]


class ChannelTests(BaseTestCase):
    def test_get_channels(self):
        pass
