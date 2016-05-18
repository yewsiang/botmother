from test_base import BaseTestCase
from app.accounts import TelegramAccountManager, AccountManager, User
from app.knowledgebase import Channel
from app import db
from sqlalchemy.exc import IntegrityError

#from app.telegram import Command, User, Start


# Create a fake bot that stores the messages sent to the user in a variable
# to allow us to test the messages sent to the user
# telepot uses self.bot.sender.sendMessage(msg) to send messages to user
def testSendMessage(self, msg):
    #self.messages.append(msg)
    return


class FakeBot:
    def __init__(self):
        self.messages = []
        self.sender = object
        self.bot.sender = object
        #self.bot.sender.sendMessage = testSendMessage(self)
        assert False


class TelegramTests(BaseTestCase):
    def test_process_command(self):
        '''
        Tests that users commands are sent properly
        '''
        fakeBot = FakeBot()
        #fakeBot.bot.sender.sendMessage("hello")
        #assert fakeBot.messages[0] == "hello"
        assert False


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
