from test_base import BaseTestCase
from app.accounts import TelegramAccountManager, AccountManager, User
from app.knowledgebase import Channel
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
    def test_ask_valid_question(self):
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # ensure that we get the right question id returned
        assert KBManager.ask_question(123, 'cs2100', "hi") == 1

    def test_ask_blank_question(self):
        u1 = self.create_user(123, 0)
        u1.channels.append(Channel(name='cs2100'))
        db.session.add(u1)
        db.session.commit()

        # ensure that we get the right question id returned
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "")

    def test_ask_question_from_non_user(self):
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "a")

    def test_ask_question_for_nonexistent_channel(self):
        u1 = self.create_user(123, 0)
        self.assertRaises(ValueError, KBManager.ask_question, 123, 'cs2100', "a")

    def test_ask_too_long_question(self):
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
