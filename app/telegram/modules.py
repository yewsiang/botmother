from .commands import State
from app.accounts import AccountManager
from app.knowledgebase import KBManager


class Modules:
    '''
    This class handles all User's request that involves modules.
    1) Check the modules in their subscribed list
    2) Check the modules that are available
    3) Add modules to their subscribed list
    4) Delete modules from their list
    '''
    # /me - When User types /me to find out the modules that they've subscribed to
    @classmethod
    def me_command(cls, bot):
        # List of modules that have been subscribed by user
        if bot.subscribed_channels == []:
            bot.sender.sendMessage("You have not subscribed to any mods.\n"
                "/<module code> to add a module (E.g /PAP1000 adds the module PAP1000)")
        else:
            # Send user's telegram id and retrieve a list of modules
            list_of_subscribed_channels = ""
            for channel in bot.subscribed_channels:
                list_of_subscribed_channels += str(channel).upper() + " "

            bot.sender.sendMessage('Your modules subscribed are ' + list_of_subscribed_channels)

    # /module - When User types /module to retrieve all modules available for subscription
    @classmethod
    def module_command(cls, bot):
        # Retrieve all the modules that are available for subscription
        list_of_all_modules = KBManager.retrieve_all_modules()
        string_to_send = "Modules available:  "
        for module in list_of_all_modules:
            string_to_send += "/" + str(module).upper() + "  "
        # Send the user a list of modules with "/" appended - easier to subscribe
        bot.sender.sendMessage(string_to_send)

    # /add - When User types /add
    # However, we are not supporting /add but /<module code> command. This is just for fun.
    @classmethod
    def add_command(cls, bot):
        # Redirect people to /<module code>
        bot.sender.sendMessage("Woah. How do you know there is a /add when we didn't tell you"
            " there is? Please use /<module code> to add the module of your choice :)")

    # /<module code> - When User types /<module code> in the expectation that it will add <module code>
    # into their list of subscribed modules
    @classmethod
    def module_code_command(cls, bot, command):
        # Say, Users do this "/MA1234"
        # We must search if "MA1234" is a valid module
        module_code = command[1:]
        list_of_all_modules = KBManager.retrieve_all_modules()

        # Check if it is a valid module
        module_exists = module_code in list_of_all_modules
        if (module_exists):
            # Check if the User has already subscribed to the channel
            subscribed_to_channel_already = False
            for channel in bot.subscribed_channels:
                if str(channel) == module_code:
                    subscribed_to_channel_already = True

            if subscribed_to_channel_already:
                bot.sender.sendMessage("You've subscribed to the module already :)")
            else:
                add_channel_succeed = AccountManager.add_channel(bot.telegram_id, module_code)
                if add_channel_succeed:
                    bot.sender.sendMessage("Module added to your subscription")
                else:
                    bot.sender.sendMessage("There is a problem adding your module. Please try again later :(")
        else:
            bot.sender.sendMessage("Module does not exist. /modules to see the available modules")

    # /delete - When User types /delete
    @classmethod
    def delete_command(cls, bot):
        # User wants to delete modules off his subscription list
        if bot.subscribed_channels == []:
            bot.sender.sendMessage("You have not subscribed to any mods.\n"
                "/<module code> to add a module (E.g /BRO1000 adds the module BRO1000)")
        else:
            # When User types /BRO1000, we will delete BRO1000 from HIS acc
            bot.state = State.DELETING_CHANNEL
            bot.sender.sendMessage("What module would you like to delete?")

    # State.DELETING - When User wants to delete a channel.
    # The User has already typed /delete, and is now typing /<module code> to delete <module code>
    @classmethod
    def process_deleting_channels(cls, bot, delegator_bot, command):
        print "(B) PROCESS DELETING CHANNELS"
        module_code = command[1:]
        deletedChannel = AccountManager.delete_channel(bot.telegram_id, module_code)
        if (deletedChannel):
            bot.state = State.NORMAL
            bot.sender.sendMessage("You have deleted " + module_code + " from your subscribed modules :(")
        else:
            bot.sender.sendMessage("You are not even subscribed to " + module_code)
