from test_base import BaseTestCase
from app.accounts import TelegramAccountManager, User
from app import db
from sqlalchemy.exc import IntegrityError


class ModelTests(BaseTestCase):
    def test_create_if_not_exists(self):
        '''
        Tests that the create account method works properly
        '''
        res1 = TelegramAccountManager.create_account_if_does_not_exist(123)
        res2 = TelegramAccountManager.create_account_if_does_not_exist(123)
        assert res1 is False
        assert res2 is True

    def test_unique_telegram_user_id(self):
        '''
        Tests that we can't create two users with the same telegram
        user id
        '''

        # user does not exist
        new_user = User(123, 0)
        # Add to database
        db.session.add(new_user)
        # Commit changes
        db.session.commit()

        # user does not exist
        new_user_2 = User(123, 4)
        # Add to database
        db.session.add(new_user_2)

        # Commit changes - SHOULD FAIL because of unique telegram id constraint
        self.assertRaises(IntegrityError, db.session.commit)

