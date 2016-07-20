from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from app.helpers import get_weblink_by_question_id, get_question_by_id
from app.knowledgebase import KBManager
from .points import Points
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

    # (Delayed Function)
    # Sending voting results to intere  ed parties after the vote has concluded:
    # 1) Clicked on "Vote" button
    # 2) Clicked on the keyboard with 9 numbers
    # Forum link is also sent along so that interested parties can continue the discussion
    @classmethod
    def send_answers_and_link_to_participants(cls, bot, delegator_bot, question_id, number_of_answers):
        # number_of_answers is needed because in the 15mins of voting, there may have been new answers that
        # have been submitted. It shouldn't be included.
        # After the voting has finalized, we will send the answers, votes and link to those who participated
        # Get the link to the question
        forum_link = get_weblink_by_question_id(question_id)

        # Finding the participants to send to
        question = get_question_by_id(question_id)
        answerers_user_ids = map(lambda answer: answer.user.telegram_user_id, question.answers)
        user_ids = answerers_user_ids + [question.user.telegram_user_id]

        #
        # Use a hash to add unique voter ids into a list
        hash_to_determine_uniqueness = {}
        unique_voter_ids = []
        # Getting the votes for each answer
        list_of_answer_with_votes = []
        for idx, answer in enumerate(question.answers):
            if idx < number_of_answers:
                vote_value = 0
                for vote in answer.votes.all():
                    try:
                        # If voter_id not in the hash, add it to the list of unique ids
                        # This is so that we can send messages later
                        hash_to_determine_uniqueness[vote.user.telegram_user_id]
                    except KeyError:
                        hash_to_determine_uniqueness[vote.user.telegram_user_id] = 1
                        unique_voter_ids.append(vote.user.telegram_user_id)

                    # Add the total value of the votes of each answer
                    vote_value += vote.amount

                # Append to the list of answers with votes to sort by vote value
                list_of_answer_with_votes.append([answer.text, vote_value])

        # If there are at least one vote for the top answer, award a point to the person who asked the question
        # and the person who answered
        # Asker should only receive points once
        awarded_points_to_asker_already = False
        for idx, answer in enumerate(list_of_answer_with_votes):
            if idx < number_of_answers:
                # Award points only if there is a vote to an answer
                if list_of_answer_with_votes[idx][1] != 0:
                    # Award points to the asker if haven't already
                    if not awarded_points_to_asker_already:
                        Points.award_points(question.user.telegram_user_id, 1)
                        awarded_points_to_asker_already = True
                    # Award points to the answerer
                    Points.award_points(answerers_user_ids[idx], 1)

        # Sorting the list of answers by vote_values
        list_of_answer_with_votes.sort(key=lambda ans_tuple: ans_tuple[1], reverse=True)

        #
        # Creating the text to send to the Users
        text_to_send = ("<b>" + question.channel.name.upper() + "</b>\n"
                "Question: " + question.text + "\n"
                "Answers:\n")
        for idx, ans_tuple in enumerate(list_of_answer_with_votes):
            # Do not add more answers than number_of_answers
            text_to_send += (str(idx + 1) + ". " + ans_tuple[0] + "\n"
                "<b>Upvotes</b>: " + str(ans_tuple[1]) + "\n\n")
        text_to_send += "The voting results and answers are out! Go to the forum to continue the discussion :)"

        # Send to the participants
        user_ids = user_ids + unique_voter_ids
        for user_id in user_ids:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Link to Forum', url=forum_link)]
                 ])
            delegator_bot.sendMessage(user_id, text_to_send, reply_markup=markup, parse_mode='HTML')
