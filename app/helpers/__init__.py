from app import db
import app.accounts

# Create the association table between channels and users
user_channels_table = db.Table('userchannels', db.Model.metadata,
                               db.Column('user_id', db.Integer,
                                         db.ForeignKey('users.id')),
                               db.Column('channel_id', db.Integer,
                                         db.ForeignKey('channels.id'))
                               )


def get_user_by_telegram_id(telegram_user_id):
    '''
    Helper method that checks the database for a user with a
    particular telegram_user_id and returns it if it exists,
    or returns None if not
    '''
    return db.session.query(app.accounts.User).\
        filter(app.accounts.User.telegram_user_id == telegram_user_id).first()


def get_question_by_id(question_id):
    '''
    Simple helper to return any question in the database that matches
    the id given
    '''
    return db.session.query(app.knowledgebase.Question).get(question_id)


def get_answer_by_id(answer_id):
    '''
    Simple helper to return any answer in the database that matches
    the id given
    '''
    return db.session.query(app.knowledgebase.Answer).get(answer_id)
