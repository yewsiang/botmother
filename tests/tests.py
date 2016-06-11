from test_base import BaseTestCase
from app.helpers import get_answer_by_id
from app.accounts import TelegramAccountManager, AccountManager, User
from app.knowledgebase import Channel, Question
from app import db
from sqlalchemy.exc import IntegrityError
from app.knowledgebase import KBManager

from app.telegram import Command


# Create a fake bot that stores the messages sent to the user in a variable
# to allow us to test the messages sent to the user
# telepot uses self.bot.sender.sendMessage(msg) to send messages to user
def test_send_message(self, msg):
    #self.messages.append(msg)
    return


# Compare 2 lists of messages and make sure they are the same
def compare_two_lists_sequentially(self, incoming_messages, expected_messages):
    if (len(incoming_messages) != len(expected_messages)):
        return False
    are_identical_messages = True
    for i, incoming_message in enumerate(incoming_messages):
        if (incoming_message != expected_messages[i]):
            are_identical_messages = False
    return are_identical_messages


class FakeBot:
    def __init__(self):
        self.messages = []
        self.sender = object
        self.bot.sender = object
        #self.bot.sender.sendMessage = testSendMessage(self)
        assert False

'''
class TelegramTests(BaseTestCase):
    def test_process_command(self):
        # Tests that users commands are sent properly
        fakeBot = FakeBot()
        #fakeBot.bot.sender.sendMessage("hello")
        #assert fakeBot.messages[0] == "hello"
        assert False
'''


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

        question_id = KBManager.ask_question(123, 'cs2100', 'what is life?')

        # add all the answers
        for i in answers:
            KBManager.add_answer_to_question(question_id, u2.telegram_user_id, i)

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

        # check that their unordered versions are the same
        assert set(answers) == set(found_answers)

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
