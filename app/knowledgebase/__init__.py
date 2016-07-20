from .models import Question, Answer, Vote, Comment, Channel, Faculty
from app import db, app
from app.accounts import User
from app.helpers import get_user_by_telegram_id
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.helpers import get_user_by_telegram_id, get_answer_by_id
from flask import url_for
'''
Constants
'''
max_questions_per_day = 20


class KBManager(object):
    #
    # FACULTIES
    #
    @staticmethod
    def retrieve_all_faculties():
        '''
        Gets a list of all faculaties currently in the system
        '''
        return db.session.query(Faculty).all()

    @staticmethod
    def retrieve_all_modules_from_faculty(faculty_name):
        '''
        Looks for a faculty with the given name and returns all associated
        modules
        '''
        fac = db.session.query(Faculty).filter(Faculty.name == faculty_name).first()
        if fac is not None:
            # Force non-lazy
            return list(fac.channels)
        else:
            return None

    @staticmethod
    def get_module_activity(module_name):
        '''
        Returns a tuple of (Number of Users, Time since last question) given
        a module code
        '''
        mod = db.session.query(Channel).filter(Channel.name == module_name).first()
        if mod is not None:
            num_users = len(mod.users)

            questions = mod.questions
            if questions.count() > 0:
                # if we have at least one asked question - return the time difference between
                # now and when the questions was asked
                by_date_created = mod.questions.order_by(Question.date_created)
                question_with_latest_date = by_date_created.first()
                time_difference = datetime.now() - question_with_latest_date.date_created
                return (num_users, time_difference)
            else:
                # If we have no questions - no timedelta to return
                return (num_users, None)
        else:
            return None

    #
    # ASK QUESTIONS
    #
    @staticmethod
    def retrieve_all_modules():
        '''
        Gets all the modules that can be subscribed to - by name
        '''
        return [name[0] for name in db.session.query(Channel.name).all()]

    @staticmethod
    def can_user_ask_question(telegram_user_id):
        '''
        Returns true/false based on whether the
        number of questions per day has been exceeded for this user
        '''
        user = get_user_by_telegram_id(telegram_user_id)
        if user is not None:
            # define a simple filter to get questions from the last day
            def date_filter(question):
                return question.date_created >= (datetime.utcnow() - timedelta(days=1))

            filtered_questions = filter(date_filter, user.questions)

            # check if we have exceeded the number of questions we can have today
            return len(filtered_questions) <= max_questions_per_day

        else:
            raise ValueError('User does not exist!')

    @staticmethod
    def ask_question(telegram_user_id, channel_name, question_text):
        '''
        This method checks that the question asked is valid,
        if the user exists, and if so, adds that question to the
        questions asked by the user, and returns the question id to the
        function caller for reference
        '''
        if question_text == "":
            raise ValueError("Cannot ask a question with no content!")
        else:
            user = db.session.query(User).filter(
                User.telegram_user_id == telegram_user_id).first()

            if user is not None:
                channel = db.session.query(Channel).filter(
                    Channel.name == channel_name).first()

                if channel is not None:
                    # add the question to the channel and commit
                    new_question = Question(question_text)
                    channel.questions.append(new_question)
                    db.session.add(channel)
                    db.session.commit()

                    # add the question to the user and return the question id
                    user.questions.append(new_question)
                    db.session.add(user)
                    db.session.commit()
                    return new_question.id

                else:
                    raise ValueError('Channel does not exist!')

            else:
                raise ValueError('User does not exist, cannot ask question!')

    @staticmethod
    def change_question_state(question_id, new_state):
        '''
        Changes the state of a question - depending on
        what's current going on.
        0 = waiting for answers, 1 = voting,  2 = not resolved + discussing, 3 = resolved + discussing
        '''
        question = db.session.query(Question).get(question_id)
        if question is not None:
            question.state = new_state
            db.session.add(question)
            db.session.commit()
        else:
            raise ValueError('Question does not exist!')

    #
    # ANSWER QUESTIONS
    #
    @staticmethod
    def can_user_answer_question(question_id, telegram_user_id):
        '''
        Checks if a user has already answered a question and
        the question has entered the voting process.
        If both are true, return False, else True
        '''
        question = db.session.query(Question).get(question_id)

        if question is not None:
            if question.state == 0:
                # the question hasn't entered the voting process, can still answer
                return True
            else:
                user = get_user_by_telegram_id(telegram_user_id)
                if user is not None:
                    # search for the matching answer
                    val = next((x for x in user.answers if x.question_id == question_id), None)
                    # None indicates that we can answer the question since
                    # we have no answers for this question
                    return val is None
                else:
                    raise ValueError('User does not exist!')
        else:
            raise ValueError('Question does not exist!')

    @staticmethod
    def retrive_all_module_objects():
        '''
        For the controller - retrives all the module OBJECTS instead of just
        the names
        '''
        return db.session.query(Channel).all()

    @staticmethod
    def get_answerers(telegram_user_id, channel_name):
        '''
        Returns all the people in the module channel
        that we should send the question to, so that we
        can get some answers. Currently this returns
        everyone in the channel

        If the channel does not exist (raises AttributeError when
        we try to do .users, throw a ValueError up the chain)
        '''
        try:
            channel_users = db.session.query(Channel).\
                filter(Channel.name == channel_name).first().users

            answerers = [user for user in channel_users
                         if user.telegram_user_id != telegram_user_id]

            return answerers

        except AttributeError:
            raise ValueError('Channel does not exist, cannot get answerers!')

    @staticmethod
    def add_answer_to_question(question_id, answerer_telegram_user_id, answer_text):
        '''
        This method checks for a valid question, answerer and valid answer_text
        and adds it to both the question and the answerer_user
        Exceptions are raised for invalid input, otherwise returns the answer
        id
        '''
        question = db.session.query(Question).get(question_id)

        if question is not None:
            answerer = db.session.query(User).filter(
                User.telegram_user_id == answerer_telegram_user_id).first()

            if answerer is not None:
                if answer_text != "":
                    # User has not confirmed his answer, hence confirmed = False
                    answer = Answer(answer_text, False)
                    # add this answer to the user who answered
                    answerer.answers.append(answer)
                    # add this answer to the question
                    question.answers.append(answer)

                    db.session.add(answerer)
                    db.session.add(question)
                    db.session.commit()
                    return answer.id

                else:
                    raise ValueError('Answer cannot be nothing!')
            else:
                raise ValueError('Answerer does not exist!')
        else:
            raise ValueError('Question does not exist!')

    @staticmethod
    def confirm_answer(answer_id):
        '''
        This method changes the confirm variable of an answer to True.
        It is called when a User has confirmed his answer on Telegram by clicking the "Yes" button.
        '''
        answer = get_answer_by_id(answer_id)
        answer.confirmed = True
        db.session.add(answer)
        db.session.commit()

    @staticmethod
    def get_answers_for_qn(question_id):
        '''
        Gets the answers so far for a particular question
        '''
        # The answers returned should preserve the order by which they came in.
        # This is because the Users will vote according to the order that was returned.
        question = db.session.query(Question).get(question_id)
        print " ----- QUESTION -----"
        print question
        if question is not None:
            sorted_answers = question.answers.order_by(Answer.id)
            print "Question: " + str(question)
            print "Answers: " + str(sorted_answers)
            confirmed_answers = filter(lambda answer: answer.confirmed, sorted_answers)
            return confirmed_answers
        else:
            raise ValueError('Question does not exist!')

    #
    # VOTE ON ANSWERS
    #
    @staticmethod
    def get_voters_and_answers_for_qn(question_id):
        '''
        Convenience function to get both the voters and answers for
        a particular question.
        Returned as tuple of (xs of User), (xs of Answer)
        '''
        voters = KBManager.get_voters_for_qn_answers(question_id)
        answers = KBManager.get_answers_for_qn(question_id)
        return (voters, answers)

    @staticmethod
    def get_voters_for_qn_answers(question_id):
        '''
        Get the people that need to vote on a particular set of answers
        for a particular question. Current behavior is EVERYONE who is not
        an answerer OR the question asker themselves will be in this list
        '''
        answers = KBManager.get_answers_for_qn(question_id)
        if answers is not None:
            # get the list of user ids
            user_ids = map(lambda x: x.user_id, answers)

            # get the actual question
            question = db.session.query(Question).get(question_id)

            # append the asker of the question to the list
            user_ids.append(question.user_id)

            # get the channel id
            channel_id = question.channel_id

            # get the channel
            channel = db.session.query(Channel).get(channel_id)

            if channel is not None:
                # get list of users in channel
                users = channel.users

                print "channel users: " + str(users)

                # return all the users that were not answerers
                return filter(lambda user: user.id not in user_ids, users)
            else:
                raise ValueError('Could not find a valid channel!')

        else:
            print "answers none!"
            return None

    # @staticmethod
    # def get_answers_to_vote_on():

    @staticmethod
    def add_vote_to_answer(answer_id, voter_telegram_id, vote_amount):
        '''
        This method checks for a valid answer and voter, then adds
        the vote object to both
        Returns True if the vote_amount is the new vote_amount (successful change)
        or False if the vote was reset to 0 (double upvote/downvote)
        '''
        answer = db.session.query(Answer).get(answer_id)

        if answer is not None:
            voter = get_user_by_telegram_id(voter_telegram_id)

            if voter is not None:
                vote_status = KBManager.user_vote_status_on_answer(answer.id, voter_telegram_id)
                # We need to check if we can even vote on this
                # I.e. we haven't voted OR we are upvoting when this is a downvote / vice versa
                is_opposite_vote = (vote_status ^ vote_amount)
                if vote_status == 0:
                    '''
                    answer and voter exist and are valid, create a new vote
                    and add it to both of them
                    '''
                    new_vote = Vote(amount=vote_amount)

                    voter.votes.append(new_vote)
                    answer.votes.append(new_vote)

                    db.session.add(voter)
                    db.session.add(answer)
                    db.session.commit()

                    #print "Adding vote"

                    return True

                elif is_opposite_vote:
                    # Change the user's vote to the correct amount
                    vote_to_change = KBManager.get_first_user_vote(answer_id, voter_telegram_id)
                    vote_to_change.amount = vote_amount
                    db.session.add(vote_to_change)
                    db.session.commit()

                    #print "Changing vote"

                    return True
                else:
                    # Remove the vote (if we double up/downvote - assume removal)

                    vote_to_remove = KBManager.get_first_user_vote(answer_id, voter_telegram_id)
                    db.session.delete(vote_to_remove)
                    db.session.commit()
                    return False

            else:
                raise ValueError('Voter is not a valid user!')
        else:
            raise ValueError('Answer cannot be found to add vote to!')

    @staticmethod
    def get_first_user_vote(answer_id, telegram_user_id):
        '''
        Returns the first vote that this user has cast for this answer
        '''
        answer = db.session.query(Answer).get(answer_id)
        user = get_user_by_telegram_id(telegram_user_id)

        if answer is not None and user is not None:
            filtered_votes = answer.votes.filter(Vote.user_id == user.id)
            if filtered_votes.count() == 0:
                # we have never voted on this
                return None
            else:
                return filtered_votes.first()
        else:
            raise ValueError('Answer or user cannot be None!')

    @staticmethod
    def vote_type(vote):
        '''
        Takes in either None or a vote. If the vote is None,
        return 0. If it's a positive vote, returns 1 (upvote). Else
        if it's negative, returns -1
        '''
        if vote is not None:
            if vote.amount > 0:
                return 1
            elif vote.amount < 0:
                return -1
            else:
                print "Should never have a 0 amount vote"
                return 0
        else:
            return 0

    @staticmethod
    def user_vote_status_on_answer(answer_id, telegram_user_id):
        '''
        Gets the user's voting status on a particular answer - with ref to the
        vote_type function
        '''
        return KBManager.vote_type(KBManager.get_first_user_vote(answer_id, telegram_user_id))





