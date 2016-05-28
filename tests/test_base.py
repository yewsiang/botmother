from flask.ext.testing import TestCase

from app import app, db
from app.accounts import User


class BaseTestCase(TestCase):
    """A base test case for flask-tracking."""

    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        return app

    def create_user(self, telegram_user_id=123, user_type=0):
        # user does not exist
        new_user = User(telegram_user_id, user_type)
        # Add to database
        db.session.add(new_user)
        # Commit changes
        db.session.commit()

        return new_user

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
