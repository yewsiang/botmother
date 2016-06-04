from .models import Question, Answer, Vote, Comment, Channel
from app import db
from app.accounts import User
from app.helpers import get_user_by_telegram_id


class KBManager(object):
    @staticmethod
    def retrieve_all_modules():
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
