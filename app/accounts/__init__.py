from .models import User
from app.knowledgebase import Channel
from app import db


class AccountManager(object):
    @staticmethod
    def get_subscribed_channels(telegram_user_id):
        '''
        Checks if a user with this telegram_user_id exists in the database
        and returns their channels
        '''
        user = db.session.query(User).filter(
            User.telegram_user_id == telegram_user_id).first()
        if user is not None:
            return user.channels
        else:
            return None

    @staticmethod
    def add_channel(telegram_user_id, channel_name):
        '''
        Checks if a user with this telegram user id exists in the database
        and if a channel with this name exists
        and adds the channel to the user

        Returns True if the operation was done successfully
        False if not
        '''
        user = db.session.query(User).filter(
            User.telegram_user_id == telegram_user_id).first()
        channel = db.session.query(Channel).filter(
            Channel.name == channel_name).first()

        if (user is not None) and (channel is not None):
            user.channels.append(channel)
            db.session.add(user)
            db.session.commit()
            return True
        else:
            return False




class TelegramAccountManager(object):
    @staticmethod
    def create_account_if_does_not_exist(telegram_user_id):
        '''
        Check if an account is present in the database
        If it is, return True and don't do anything else
        If it's not, return False and create the account
        '''
        if db.session.query(User.id).\
                filter_by(telegram_user_id=telegram_user_id).\
                scalar() is None:

            # user does not exist
            new_user = User(telegram_user_id, 0)
            # Add to database
            db.session.add(new_user)
            # Commit changes
            db.session.commit()
            # Return false to indicate we created an account
            return False
        else:
            return True
