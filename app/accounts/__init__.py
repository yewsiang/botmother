from .models import User
from app import db


class AccountManager(object):
    @staticmethod
    def get_subscribed_channels(telegram_user_id):
        pass


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


