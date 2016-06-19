from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from app.knowledgebase import KBManager
import commands

from pprint import pprint
State = commands.State


class Voting:
    '''
    This class handles the voting process after the asking and answering of questions are done.
    '''
    # Callback activated when User presses "Vote" button after the question and answers are sent to the User
    @classmethod
    def callback_vote_on_answer(cls, bot, delegator_bot, data, query_id, msg_idf=None):
        callback_type, question_id, unused, unused = data.split('_')
        bot.state = State.VOTING
        # Assumption: It is fine to store question_id temporarily in bot since the User
        # MUST click 'Vote' every time he wishes to vote on answers.
        bot.temp_vote_question_id = question_id
        # msg_id to allow editing of the "Vote" button
        bot.msg_idf = msg_idf
        markup = ReplyKeyboardMarkup(keyboard=[
                 [KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3')],
                 [KeyboardButton(text='4'), KeyboardButton(text='5'), KeyboardButton(text='6')],
                 [KeyboardButton(text='7'), KeyboardButton(text='8'), KeyboardButton(text='9')],
                 [KeyboardButton(text='0')]
             ], one_time_keyboard=True)
        bot.sender.sendMessage("Choose the answer that you are confident of. Otherwise, choose '0' :)", reply_markup=markup)

        #
        # TODO: This function needs to have a Time element as well (E.g. execute in 30 mins after Qns was sent)
        # Need to place function in appropriate place. This is simply for testing.
        #
        Voting.send_answers_and_link_to_participants(bot, delegator_bot, question_id)

    # State.VOTING - After User clicks on "Vote" button, his state changes to State.VOTING.
    # Subsequent messages will pass through this function
    @classmethod
    def process_voting(cls, bot, delegator_bot, command):
        try:
            # Check if the User clicked on the keyboard.
            # If he did, we can process his vote. Else, we may treat his messages as normal messages.
            # Attempt to cast the command into an integer
            command = int(command)
            answers = KBManager.get_answers_for_qn(bot.temp_vote_question_id)
            markup = ReplyKeyboardMarkup(keyboard=[
                     [KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3')],
                     [KeyboardButton(text='4'), KeyboardButton(text='5'), KeyboardButton(text='6')],
                     [KeyboardButton(text='7'), KeyboardButton(text='8'), KeyboardButton(text='9')],
                     [KeyboardButton(text='0')]
                 ], one_time_keyboard=True)
            if command == 0:
                # User disagrees with all of the answers
                # Reset the state
                bot.state = State.NORMAL
                bot.sender.sendMessage("Thanks for participating in the vote :)")

            elif command > 0 and command < 10 and command <= len(answers):
                # He clicked on the keyboard
                # Can now assume that he wanted to vote on one of the answers
                voted_answer = answers[command - 1]
                successfully_voted = KBManager.add_vote_to_answer(voted_answer.id, bot.telegram_id, 1)
                print voted_answer.votes
                if successfully_voted:
                    new_markup = InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="Voted!", callback_data="Voted_None_None_None")]
                          ])
                    msg_idf = (bot.telegram_id, bot.msg_idf)
                    delegator_bot.editMessageReplyMarkup(msg_idf, new_markup)
                    # Reset the state
                    bot.state = State.NORMAL
                    bot.sender.sendMessage("Thanks for participating in the vote :)")
                else:
                    bot.sender.sendMessage("There has been a problem with your vote. Please try again!", reply_markup=markup)

            else:
                # User typed an invalid integer
                bot.sender.sendMessage("That's not a valid voting number. Please try again!\n"
                    "/done if you do not wish to vote", reply_markup=markup)

        except ValueError:
            # Reset the state
            bot.state = State.NORMAL
            # Assume that the User clicked outside of the keyboard and wanted to do something else
            bot.sender.sendMessage("Click on Vote and enter a number if you wish to vote")
            # process_commands takes in a msg object with 'text' key
            commands.Command.process_commands(bot, delegator_bot, {'text': command})

    # Sending voting results to interested parties after the vote has concluded:
    # 1) Clicked on "Vote" button
    # 2) Clicked on the keyboard with 9 numbers
    # Forum link is also sent along so that interested parties can continue the discussion
    @classmethod
    def send_answers_and_link_to_participants(cls, bot, delegator_bot, question_id):
        #
        # TODO
        #
        # After the voting has finalized, we will send the answers, votes and link to
        # those who participated
        #
        markup = InlineKeyboardMarkup(inline_keyboard=[
                 [dict(text='Link to Forum', url='https://core.telegram.org/')]
             ])
        print "Wala Wala"
        # bot.sender.sendMessage("The votreply_markup=markup)
