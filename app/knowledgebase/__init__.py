from .models import Question, Answer, Vote, Comment, Channel
from app import db
from app.accounts import User
from app.helpers import get_user_by_telegram_id
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.helpers import get_user_by_telegram_id

'''
Constants
'''
max_questions_per_day = 20


class KBManager(object):
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
    def get_voters_and_answers_for_qn(question_id):
        '''
        Convenience function to get both the voters and answerers for
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

    @staticmethod
    def get_answers_for_qn(question_id):
        '''
        Gets the answers so far for a particular question
        '''
        question = db.session.query(Question).get(question_id)
        if question is not None:
            return question.answers
        else:
            raise ValueError('Question does not exist!')


    @staticmethod
    def retrieve_all_modules():
        '''
        Gets all the modules that can be subscribed to - by name
        '''
        return [name[0] for name in db.session.query(Channel.name).all()]

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
                    answer = Answer(answer_text)
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


    #@staticmethod
    #def get_answers_to_vote_on():

    @staticmethod
    def add_vote_to_answer(answer_id, voter_telegram_id, vote_amount):
        '''
        This method checks for a valid answer and voter, then adds
        the vote object to both
        '''
        answer = db.session.query(Answer).get(answer_id)

        if answer is not None:
            voter = get_user_by_telegram_id(voter_telegram_id)

            if voter is not None:
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

                return True
            else:
                raise ValueError('Voter is not a valid user!')
        else:
            raise ValueError('Answer cannot be found to add vote to!')
