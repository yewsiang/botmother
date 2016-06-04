from app.accounts import AccountManager
from app.knowledgebase import KBManager
from .message_blast import MessageBlast
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import pprint


# To track the state of the specific user
class State:
    NORMAL = 0
    DELETING_CHANNEL = 1

    ASKING_QUESTIONS = 2
    SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS = 3

    ANSWERING_QUESTIONS = 4
    CONFIRMATION_OF_ANSWER = 5

    VOTING = 6
    CHANGE_SETTINGS = 7


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
                    # "/answer - Answer questions\n"  # Changes state - May not be showing this to users
                    # "/vote - Vote on answers\n"  # Changes state - May not be showing this to users
                    "/modules - List the modules that you can subscribe to\n"
                    "/<module code> - Add a module (E.g /MOM1000 adds the module MOM1000)\n"
                    "/delete - Delete modules that you do not want to receive updates from\n"  # Changes state
                    "/settings - Change your settings (E.g notification rate)\n"  # Changes state
                    "/end - Stop the conversation :(\n")
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
            bot.sender.sendMessage(string_to_send)

            # TODO : REMOVE
            # TESTING
            #
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text='Answer Question', callback_data='question_answered')],
                     [dict(text='Link to Forum', url='https://core.telegram.org/')]
                 ])

            bot.sender.sendMessage("Testing InlineKeyboard", reply_markup=markup)
            #
            #
            #

        elif command == '/done':
            bot.state = State.NORMAL
            bot.sender.sendMessage("You are back to normal")

        elif command == '/end':
            bot.sender.sendMessage("<The End>")
            bot.close()

        else:
            # Once the general commands are catered, the command will be sent to an appropriate
            # function depending on the user's State
            if (bot.state == State.NORMAL):
                Command.process_normal_commands(bot, delegator_bot, command)
            elif (bot.state == State.DELETING_CHANNEL):
                Command.process_deleting_channels(bot, delegator_bot, command)
            elif (bot.state == State.ASKING_QUESTIONS):
                Command.process_asking_questions(bot, delegator_bot, command)
            elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
                Command.process_selecting_channel_after_asking_questions(bot, delegator_bot, command)
            elif (bot.state == State.ANSWERING_QUESTIONS):
                Command.process_answering_questions(bot, delegator_bot, command)
            elif (bot.state == State.CONFIRMATION_OF_ANSWER):
                Command.process_confirmation_of_answer(bot, delegator_bot, command)
            elif (bot.state == State.VOTING):
                Command.process_voting(bot, delegator_bot, command)
            elif (bot.state == State.CHANGE_SETTINGS):
                Command.process_change_settings(bot, delegator_bot, command)
            else:
                print "Wat?"

    # State.NORMAL - Function that will be called when the usual queries are called
    @classmethod
    def process_normal_commands(cls, bot, delegator_bot, command):
        print "(A) PROCESS NORMAL COMMANDS"
        print bot.telegram_id

        # TODO: Probably have to do pre-processing before comparing

        if command == '/ask':
            # User wants to ask questions
            bot.state = State.ASKING_QUESTIONS
            bot.sender.sendMessage("What are your questions?")

        elif command == '/answer':
            # User clicks on questions he wants to answer
            bot.state = State.ANSWERING_QUESTIONS
            bot.sender.sendMessage("What is your answer?")

        elif command == '/vote':
            # User votes on answers
            bot.state = State.VOTING
            bot.sender.sendMessage("Which answer do you think best fits your question?")

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
                # When user types /BRO1000, we will delete BRO1000 from HIS acc
                bot.state = State.DELETING_CHANNEL
                bot.sender.sendMessage('What module would you like to delete?')

        elif command == '/settings':
            # Allow people to change their settings (eg notifications)
            bot.state = State.CHANGE_SETTINGS
            bot.sender.sendMessage("What settings would you like to change?")

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
            bot.sender.sendMessage('Module Added')
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

    # State.ASKING_QUESTIONS - When user wants to ask questions for a module
    @classmethod
    def process_asking_questions(cls, bot, delegator_bot, command):
        print "(C) PROCESS ASKING QUESTIONS"
        bot.question_asked = command
        bot.state = State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS
        bot.sender.sendMessage("Which module would you like to send the question to?")

    # State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS - When user finished typing his question and is
    # selecting a channel to post the question
    @classmethod
    def process_selecting_channel_after_asking_questions(cls, bot, delegator_bot, command):
        print "(C2) PROCESS SELECTING CHANNEL AFTER ASKING QUESTIONS"
        module_code = command[1:]
        #
        # TODO: Check if the user should be allowed to ask questions
        #
        answerers = KBManager.get_answerers(bot.telegram_id, module_code)
        MessageBlast.send_question_to_answerers(bot, delegator_bot, module_code, bot.question_asked, answerers)
        bot.sender.sendMessage("Your question has been sent to the people subscribed to " + module_code.upper() +
            ". The answers will be sent back to you in 15 mins!")

    # State.ANSWERING_QUESTIONS - When user clicks on other person's questions to answer
    # TAKE NOTE: For user experience, we do not want to display all the information (all the ints)
    #
    # TODO
    #
    @classmethod
    def process_answering_questions(cls, bot, delegator_bot, command):
        print "(D) PROCESS ANSWERING QUESTIONS"
        bot.sender.sendMessage("We are in answering questions function")

    # State.CONFIRMATION_OF_ANSWER
    #
    # TODO
    #
    @classmethod
    def process_confirmation_of_answer(cls, bot, delegator_bot, command):
        print "(D2) CONFIRMATION OF ANSWERS"
        bot.sender.sendMessage("We are in confirmation of answers function")

    # State.VOTING - When user clicks on answer to vote
    # TAKE NOTE: For user experience, we do not want to display all the information (all the ints)
    #
    # TODO
    #
    @classmethod
    def process_voting(cls, bot, delegator_bot, command):
        print "(E) PROCESS VOTING"
        bot.sender.sendMessage("We are in voting function")

    @classmethod
    def process_change_settings(cls, bot, delegator_bot, command):
        print "(F) PROCESS CHANGE SETTINGS"
        bot.sender.sendMessage("We are in change settings function")
