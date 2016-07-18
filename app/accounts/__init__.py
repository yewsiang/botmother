from .models import User, Role
from app.knowledgebase import Channel
from app.helpers import get_user_by_telegram_id
from app import db
from random import randint
from datetime import datetime, timedelta
from flask.ext.security import login_user, logout_user


class AccountManager(object):
    @staticmethod
    def get_user_by_telegram_id(telegram_user_id):
        '''
        Helper method that checks the database for a user with a
        particular telegram_user_id and returns it if it exists,
        or returns None if not
        '''
        return db.session.query(User).\
            filter(User.telegram_user_id == telegram_user_id).first()

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
        adds the channel to the user

        Returns True if the operation was done successfully
        False if not
        '''
        user = db.session.query(User).filter(
            User.telegram_user_id == telegram_user_id).first()
        print "searching for " + str(channel_name)
        channel = db.session.query(Channel).filter(
            Channel.name == channel_name).first()

        # TODO: Remove Edits
        # and (channel is not None):
        if (user is not None and channel is not None):
            user.channels.append(channel)
            db.session.add(user)
            db.session.commit()
            return True
        else:
            if (user is None):
                print 'User none'
            if (channel is None):
                print 'Channel is none'

            return False

    @staticmethod
    def delete_channel(telegram_user_id, channel_name):
        '''
        Checks if a user with this telegram user id exists in the database
        and if a channel with this name exists
        delete it from the user.

        Returns True if the operation was done successfully
        False if not
        '''
        user = db.session.query(User).filter(
            User.telegram_user_id == telegram_user_id).first()
        print "searching for " + str(channel_name)

        # TODO: Remove Edits
        if (user is not None):
            length_before = len(user.channels)
            # removes any channels with "channel_name"
            user.channels = [
                channel for channel in user.channels if channel.name != channel_name]
            db.session.add(user)
            db.session.commit()
            length_after = len(user.channels)
            if (length_before > length_after):
                return True
            else:
                return False
        else:
            print 'User none'

            return False


class TelegramAccountManager(object):
    @staticmethod
    def create_account_if_does_not_exist(telegram_user_id, name=""):
        '''
        Check if an account is present in the database
        If it is, return True and don't do anything else
        If it's not, return False and create the account
        '''
        if db.session.query(User.id).\
                filter_by(telegram_user_id=telegram_user_id).\
                scalar() is None:

            # user does not exist
            new_user = User(telegram_user_id=telegram_user_id, user_type=0)
            # Add a name to the user
            new_user.name = name
            # Add to database
            db.session.add(new_user)
            # Commit changes
            db.session.commit()

            # Return false to indicate we created an account
            return False
        else:
            return True

    @staticmethod
    def get_points(telegram_user_id):
        '''
        Simple get of the user's current points.
        If no user by this id - return none
        '''
        user = get_user_by_telegram_id(telegram_user_id)
        if user is not None:
            return user.points
        else:
            return None

    @staticmethod
    def award_points(telegram_user_id, points):
        '''
        Adds points to user if user exists, otherwise returns none
        '''
        user = get_user_by_telegram_id(telegram_user_id)
        if user is not None:
            user.points = user.points + points
            db.session.add(user)
            db.session.commit()
        else:
            return None

    @staticmethod
    def generate_and_store_otp(telegram_user_id):
        '''
        For the given user - stores a randomly generated OTP and expiry
        '''
        user = get_user_by_telegram_id(telegram_user_id)
        if user is not None:
            otp = randint(100000, 999999)
            user.current_otp = otp
            user.otp_expiry = datetime.now() + timedelta(seconds=60)
            db.session.add(user)
            db.session.commit()
            return otp
        else:
            return None

    @staticmethod
    def merge_accounts_through_otp(current_user, otp):
        '''
        Looks through database for a user with the input otp.
        If it sees a user with an unexpired OTP - merges the two users into one.
        '''
        telegram_user_with_otp = db.session.query(User).filter(User.current_otp == otp).first()
        if telegram_user_with_otp is not None:
            if telegram_user_with_otp.otp_expiry > datetime.now():
                # If we have a valid user with the OTP and it's unexpired,
                # merge the two accounts
                success = TelegramAccountManager.merge_accounts(current_user, telegram_user_with_otp)
                print "Merge success"
                return telegram_user_with_otp
            else:
                print "Merge failure - expired OTP"
                return None
        else:
            print "Merge failure - no user with OTP"
            return None

    @staticmethod
    def merge_accounts(web_user, telegram_user):
        '''
        Given a web-user and a telegram user - merges the important information from the
        telegram user into the web user and then deletes the web user
        '''
        with db.session.no_autoflush:
            temp_dict = {}
            temp_dict['name'] = web_user.name

            # Add gamification points together
            temp_dict['points'] = telegram_user.points + web_user.points

            # Merge security info
            temp_dict['email'] = web_user.email
            temp_dict['password'] = web_user.password
            temp_dict['active'] = web_user.active
            temp_dict['confirmed_at'] = web_user.confirmed_at
            temp_dict['roles'] = web_user.roles

            # Delete the web account
            db.session.delete(web_user)
            db.session.commit()

            # The web user will have a name - the telegram user will not
            telegram_user.name = temp_dict['name']

            # Add gamification points together
            telegram_user.points = temp_dict['points']

            # Merge security info
            telegram_user.email = temp_dict['email']
            telegram_user.password = temp_dict['password']
            telegram_user.active = temp_dict['active']
            telegram_user.confirmed_at = temp_dict['confirmed_at']
            telegram_user.roles = temp_dict['roles']

            # Relationship merging as needed

            # Add the changed telegram acct
            db.session.add(telegram_user)
            db.session.commit()

            # Return success
            return True


