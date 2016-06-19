from .commands import State


class Settings:
    '''
    This class handles all the settings commands.
    '''
    # /settings - User types /settings to change settings
    @classmethod
    def settings_command(cls, bot):
        # Allow Users to change their settings (eg notifications)
        bot.state = State.CHANGE_SETTINGS
        bot.sender.sendMessage("What settings would you like to change?")

    # State.CHANGE_SETTINGS - User has typed /settings, and is now changing settings with new messages
    @classmethod
    def process_change_settings(cls, bot, delegator_bot, command):
        #
        # TODO
        #
        print "(F) PROCESS CHANGE SETTINGS"
        bot.sender.sendMessage("We are in change settings function")
