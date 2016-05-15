from test_base import BaseTestCase
from app.accounts import TelegramAccountManager


class ModelTests(BaseTestCase):
    def test_create_if_not_exists(self):
        '''
        Tests that the create account method works properly
        '''
        res1 = TelegramAccountManager.create_account_if_does_not_exist(123)
        res2 = TelegramAccountManager.create_account_if_does_not_exist(123)
        assert res1 is False
        assert res2 is True
