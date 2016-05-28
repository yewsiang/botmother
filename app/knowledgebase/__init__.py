from .models import Question, Answer, Vote, Comment, Channel
from app import db
from app.accounts import User


class KBManager(object):
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

'''
    @staticmethod
    def add_answer_to_question(question_id, answerer_telegram_user_id, answer):
'''
