from app.accounts import AccountManager
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
from .modules import Modules
from .questions import AskingQuestions, AnsweringQuestions
from .voting import Voting
from .settings import Settings
from .help import Help


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

        # ------------ DEBUGGING PURPOSES -----------
        if command == '/':
            print "bot.State = " + str(bot.state)
        # --------------  REMOVE LATER --------------

        if command == '/help':
            # /help - When User types /help in any State
            Help.help_according_to_state(bot)

        elif command == '/me':
            # /me - When User types /me to find out the modules that they've subscribed to
            Modules.me_command(bot)

        elif command == '/modules':
            # /module - When User types /module to retrieve all modules available for subscription
            Modules.modules_command(bot)

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
                Modules.process_deleting_channels(bot, delegator_bot, command)

            # AskingQuestions
            elif (bot.state == State.ASKING_QUESTIONS):
                # State.ASKING_QUESTIONS - When User types in his question and it is sent to this function
                AskingQuestions.process_asking_questions(bot, delegator_bot, command)
            elif (bot.state == State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS):
                # State.SELECTING_CHANNEL_AFTER_ASKING_QUESTIONS - When user finished typing his question and is
                # selecting a channel to post the question
                AskingQuestions.process_selecting_channel_after_asking_questions(bot, delegator_bot, command)

            # AnswerQuestions
            elif (bot.state == State.ANSWERING_QUESTIONS):
                # State.ANSWERING_QUESTIONS - User clicks "Answer Question" and enters his answer.
                AnsweringQuestions.process_confirmation_of_answer(bot, delegator_bot, command)

            # Voting
            elif (bot.state == State.VOTING):
                # State.VOTING - When user clicks on answer to vote
                Voting.process_voting(bot, delegator_bot, command)

            # Settings
            elif (bot.state == State.CHANGE_SETTINGS):
                # State.CHANGE_SETTINGS - User has typed /settings, and is now changing settings with new messages
                Settings.process_change_settings(bot, delegator_bot, command)
            else:
                print "ERROR: There should not be any other states other than those listed"

    # State.NORMAL - Function that will be called when the usual queries are called
    @classmethod
    def process_normal_commands(cls, bot, delegator_bot, command):
        print "(A) PROCESS NORMAL COMMANDS"
        print bot.telegram_id

        if command == '/ask':
            # /ask - User initiates asking questions by typing "/ask"
            AskingQuestions.ask_command(bot)

        elif command == '/add':
            # /add - When User types /add
            # However, we are not supporting /add but /<module code> command. This is just for fun.
            Modules.add_command(bot)

        elif command == '/delete':
            # /delete - When User types /delete
            Modules.delete_command(bot)

        elif command == '/settings':
            Settings.settings_command(bot)

        elif command[:1] == '/':
            # /<module code> - When User types /<module code> in the expectation that it will add <module code>
            # into their list of subscribed modules
            Modules.module_code_command(bot, command)

        else:
            # User probably typed something invalid
            bot.sender.sendMessage("You're not allowed to do this.\n/help for help :)")
        return
