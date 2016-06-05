from app.accounts import AccountManager
from app.knowledgebase import KBManager
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import pprint


# To track the state of the specific user
class State:
    NORMAL = 0
    DELETING_CHANNEL = 1

    ASKING_QUESTIONS = 2
    SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS = 3

    ANSWERING_QUESTIONS = 5

    VOTING = 6
    CHANGE_SETTINGS = 7


# Placed here because fuck python
from .questions import AskingQuestions, AnsweringQuestions


class Command:
    '''
    All commands are first passed into this function
    A second function will be called depending on the State at which the user is in
    The initial commands (/help, /done, /me, /modules) must be supported REGARDLESS of STATE
    '''
    @classmethod
    def process_commands(cls, bot, delegator_bot, command):
        print "(1) PROCESS COMMANDS"
        bot.subscribed_channels = AccountManager.get_subscribed_channels(bot.telegram_id)
        print bot.subscribed_channels

        # -------- DEBUGGING PURPOSES -------
        if command == '/':
            print "bot.State = " + bot.State
        # ----------  REMOVE LATER ----------

        if command == '/help':
            # DEPENDING on the STATE of the User, provide different help commands
            # TODO
            if bot.state == State.NORMAL:
                bot.sender.sendMessage("/help - List commands that you can\n"
                    "/me - List the modules that you are subscribed to\n"
                    "/ask - Ask questions!\n"  # Changes state
                    "/modules - List the modules that you can subscribe to\n"
                    "/<module code> - Add a module (E.g /MOM1000 adds the module MOM1000)\n"
                    "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                    "/settings - Change your settings (E.g notification rate)")  # Changes state
            elif (bot.state == State.DELETING_CHANNEL):
                bot.sender.sendMessage("/<module code> - Delete a module that you are subscribed to\n"
                    "/done - Done with deleting modules\n")
            elif (bot.state == State.ASKING_QUESTIONS):
                bot.sender.sendMessage("Send a question to those who are subscribed to the particular module\n"
                    "/done - Done with asking questions\n")
            elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
                bot.sender.sendMessage("/<module code> - Send the question that you've asked to the people"
                    "subscribed to this particular module\n")
            elif (bot.state == State.ANSWERING_QUESTIONS):
                bot.sender.sendMessage("/help for ANSWERING_QUESTIONS")
            elif (bot.state == State.VOTING):
                bot.sender.sendMessage("/help for VOTING")
            elif (bot.state == State.CHANGE_SETTINGS):
                bot.sender.sendMessage("/help for CHANGE_SETTINGS")
            else:
                print "Wat?"

        elif command == '/me':
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

        elif command == '/modules':
            # Retrieve all the modules that are available for subscription
            list_of_all_modules = KBManager.retrieve_all_modules()
            string_to_send = "Modules available:  "
            for module in list_of_all_modules:
                string_to_send += "/" + str(module).upper() + "  "
            # Send the user a list of modules with "/" appended - easier to subscribe
            bot.sender.sendMessage(string_to_send)

        elif command == '/done':
            # Go back to NORMAL state from any state
            bot.state = State.NORMAL
            bot.sender.sendMessage("Done :)! /help for help!")

        else:
            # Once the general commands are catered, the command will be sent to an appropriate
            # function depending on the user's State
            if (bot.state == State.NORMAL):
                Command.process_normal_commands(bot, delegator_bot, command)
            elif (bot.state == State.DELETING_CHANNEL):
                Command.process_deleting_channels(bot, delegator_bot, command)

            # Handled by the AskingQuestions class
            elif (bot.state == State.ASKING_QUESTIONS):
                Command.process_asking_questions(bot, delegator_bot, command)
            elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
                Command.process_selecting_channel_after_asking_questions(bot, delegator_bot, command)

            # Handled by the AnswerQuestions class
            elif (bot.state == State.ANSWERING_QUESTIONS):
                Command.process_confirmation_of_answer(bot, delegator_bot, command)

            elif (bot.state == State.VOTING):
                Command.process_voting(bot, delegator_bot, command)
            elif (bot.state == State.CHANGE_SETTINGS):
                Command.process_change_settings(bot, delegator_bot, command)
            else:
                print "ERROR: There should not be any other states other than those listed"

    # State.NORMAL - Function that will be called when the usual queries are called
    @classmethod
    def process_normal_commands(cls, bot, delegator_bot, command):
        print "(A) PROCESS NORMAL COMMANDS"
        print bot.telegram_id

        if command == '/ask':
            # User wants to ask questions
            bot.state = State.ASKING_QUESTIONS
            bot.sender.sendMessage("What are your questions?")

        elif command == '/add':
            # Redirect people to /<module code>
            bot.sender.sendMessage("Woah. How do you know there is a /add when we didn't tell you"
                " there is? Please use /<module code> to add the module of your choice :)")

        elif command == '/delete':
            # User wants to delete modules off his subscription list
            if bot.subscribed_channels == []:
                bot.sender.sendMessage("You have not subscribed to any mods.\n"
                    "/<module code> to add a module (E.g /BRO1000 adds the module BRO1000)")
            else:
                # When User types /BRO1000, we will delete BRO1000 from HIS acc
                bot.state = State.DELETING_CHANNEL
                bot.sender.sendMessage("What module would you like to delete?")

        elif command == '/settings':
            # Allow Users to change their settings (eg notifications)
            bot.state = State.CHANGE_SETTINGS
            bot.sender.sendMessage("What settings would you like to change?")

        elif command[:1] == '/':
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

        else:
            # User probably typed something invalid
            bot.sender.sendMessage("You're not allowed to do this.\n/help for help :)")
        return

    # State.DELETING - When user wants to delete a channel
    @classmethod
    def process_deleting_channels(cls, bot, delegator_bot, command):
        print "(B) PROCESS DELETING CHANNELS"
        module_code = command[1:]
        deletedChannel = AccountManager.delete_channel(bot.telegram_id, module_code)
        if (deletedChannel):
            bot.sender.sendMessage("You have deleted " + module_code + " from your subscribed modules :(")
        else:
            bot.sender.sendMessage("You are not even subscribed to " + module_code)

    @classmethod
    def process_asking_questions(cls, bot, delegator_bot, command):
        AskingQuestions.process_asking_questions(bot, delegator_bot, command)

    @classmethod
    def process_selecting_channel_after_asking_questions(cls, bot, delegator_bot, command):
        AskingQuestions.process_selecting_channel_after_asking_questions(bot, delegator_bot, command)

    @classmethod
    def process_confirmation_of_answer(cls, bot, delegator_bot, command):
        AnsweringQuestions.process_confirmation_of_answer(bot, delegator_bot, command)

    # State.VOTING - When user clicks on answer to vote
    # TAKE NOTE: For user experience, we do not want to display all the information (all the ints)
    @classmethod
    def process_voting(cls, bot, delegator_bot, command):
        #
        # TODO
        #
        print "(E) PROCESS VOTING"
        bot.sender.sendMessage("We are in voting function")

    @classmethod
    def process_change_settings(cls, bot, delegator_bot, command):
        #
        # TODO
        #
        print "(F) PROCESS CHANGE SETTINGS"
        bot.sender.sendMessage("We are in change settings function")
