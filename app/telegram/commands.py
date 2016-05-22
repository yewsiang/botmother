from app.accounts import AccountManager
import pprint


# To track the state of the specific user
class State:
    NORMAL = 0
    DELETING_CHANNEL = 1
    ASKING_QUESTIONS = 2
    ANSWERING_QUESTIONS = 3
    VOTING = 4
    CHANGE_SETTINGS = 5


class Command:
    # All commands are first passed into this function
    # A second function will be called depending on the State at which the user is in
    @classmethod
    def process_commands(cls, bot, command):
        print "(1) PROCESS COMMANDS"
        if (bot.state == State.NORMAL):
            Command.process_normal_commands(bot, command)

        elif (bot.state == State.DELETING_CHANNEL):
            Command.process_deleting_channels(bot, command)

        elif (bot.state == State.ASKING_QUESTIONS):
            Command.process_asking_questions(bot, command)

        elif (bot.state == State.ANSWERING_QUESTIONS):
            Command.process_answering_questions(bot, command)

        elif (bot.state == State.VOTING):
            Command.process_voting(bot, command)

        elif (bot.state == State.CHANGE_SETTINGS):
            Command.process_change_settings(bot, command)

        else:
            print "Wat?"

    # State.NORMAL - Function that will be called when the usual queries are called
    @classmethod
    def process_normal_commands(cls, bot, command):
        print "(A) PROCESS NORMAL COMMANDS"
        subscribed_channels = AccountManager.get_subscribed_channels(bot.telegram_id)
        print bot.telegram_id
        print subscribed_channels

        # TODO: Probably have to do pre-processing before comparing

        if command == '/help':
            bot.sender.sendMessage("/help - List commands that you can\n"
                "/me - List the modules that you are subscribed to\n"
                "/ask - Ask questions!\n"  # Changes state
                # "/answer - Answer questions\n"  # Changes state - May not be showing this to users
                # "/vote - Vote on answers\n"  # Changes state - May not be showing this to users
                "/modules - List the modules that you can subscribe to\n"
                "/<module code> - Add a module (E.g /MOM1000 adds the module MOM1000)\n"
                "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                "/settings - Change your settings (E.g notification rate)\n"  # Changes state
                "/end - Stop the conversation :(\n")

        elif command == '/ask':
            # User wants to ask questions
            bot.state = State.ASKING_QUESTIONS

        elif command == '/answer':
            # User clicks on questions he wants to answer
            bot.state = State.ANSWERING_QUESTIONS

        elif command == '/vote':
            # User votes on answers
            bot.state = State.VOTING

        elif command == '/me':
            # List of modules that have been subscribed by user
            if subscribed_channels == []:
                bot.sender.sendMessage("You have not subscribed to any mods.\n"
                    "/<module code> to add a module (E.g /PAP1000 adds the module PAP1000)")
            else:
                # Send user's telegram id and retrieve a list of modules
                list_of_subscribed_channels = ""
                for channel in subscribed_channels:
                    list_of_subscribed_channels += channel + " "

                bot.sender.sendMessage('Your modules subscribed are ' + list_of_subscribed_channels)

        elif command == '/modules':
            # TODO
            # Retrieve all the modules
            bot.sender.sendMessage("These are the modules that you can subscribe to ...")

        elif command == '/add':
            # Redirect people to /<module code>
            bot.sender.sendMessage("Woah. How do you know there is a /add when we didn't tell you"
                " there is? Please use /<module code> to add the module of your choice :)")

        elif command == '/delete':
            # User wants to delete modules off his subscription list
            if subscribed_channels == []:
                bot.sender.sendMessage("You have not subscribed to any mods.\n"
                    "/<module code> to add a module (E.g /BRO1000 adds the module BRO1000)")
            else:
                # When user types /BRO1000, we will delete BRO1000 from HIS acc
                bot.state = State.DELETING_CHANNEL
                bot.sender.sendMessage('What module would you like to delete?')

        elif command == '/settings':
            # Allow people to change their settings (eg notifications)
            bot.state = State.CHANGE_SETTINGS
            bot.sender.sendMessage("What settings would you like to change?")

        elif command == '/end':
            bot.sender.sendMessage("<The End>")
            bot.close()

        else:
            # Say, people do this "/MA1234"
            # We must search if "MA1234" is a valid module
            module_code = command[1:]
            # moduleExists = checkIfModuleExists(moduleCode)
            module_exists = True
            if (module_exists):
                add_channel_succeed = AccountManager.add_channel(bot.telegram_id, module_code)
                print "Adding channel succeeded?"
                print add_channel_succeed
            else:
                bot.sender.sendMessage('Mod does not exist. Check /modules to see the available modules')
            bot.sender.sendMessage('End of Adding module')
        return

    # State.DELETING - When user wants to delete a channel
    @classmethod
    def process_deleting_channels(cls, bot, command):
        print "(B) PROCESS DELETING CHANNELS"
        bot.sender.sendMessage("We are in deleting function")

    # State.ASKING_QUESTIONS - When user wants to ask questions for a module
    @classmethod
    def process_asking_questions(cls, bot, command):
        print "(C) PROCESS ASKING QUESTIONS"
        bot.sender.sendMessage("We are in asking questions function")

    # State.ANSWERING_QUESTIONS - When user clicks on other person's questions to answer
    # TAKE NOTE: For user experience, we do not want to display all the information (all the ints)
    @classmethod
    def process_answering_questions(cls, bot, command):
        print "(D) PROCESS ANSWERING QUESTIONS"
        bot.sender.sendMessage("We are in answering questions function")

    # State.VOTING - When user clicks on answer to vote
    # TAKE NOTE: For user experience, we do not want to display all the information (all the ints)
    @classmethod
    def process_voting(cls, bot, command):
        print "(E) PROCESS VOTING"
        bot.sender.sendMessage("We are in voting function")

    @classmethod
    def process_change_settings(cls, bot, command):
        print "(F) PROCESS CHANGE SETTINGS"
        bot.sender.sendMessage("We are in change settings function")
