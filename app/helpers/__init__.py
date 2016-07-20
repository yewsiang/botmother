from app import db
import app.accounts

# Create the association table between channels and users
user_channels_table = db.Table('userchannels', db.Model.metadata,
                               db.Column('user_id', db.Integer,
                                         db.ForeignKey('users.id')),
                               db.Column('channel_id', db.Integer,
                                         db.ForeignKey('channels.id'))
                               )

def get_weblink_by_question_id(question_id):
    '''
    Given a question_id, it would generate the link that would lead to the question
    '''
    weblink = "botmother.themetamorph.net/knowledgebase/" + str(question_id)
    return weblink

def get_user_by_telegram_id(telegram_user_id):
    '''
    Helper method that checks the database for a user with a
    particular telegram_user_id and returns it if it exists,
    or returns None if not
    '''
    return db.session.query(app.accounts.User).\
        filter(app.accounts.User.telegram_user_id == telegram_user_id).first()


def get_user_by_id(db_id):
    return db.session.query(app.accounts.User).get(db_id)


def get_question_by_id(question_id):
    '''
    Simple helper to return any question in the database that matches
    the id given
    '''
    return db.session.query(app.knowledgebase.Question).get(question_id)


def get_all_questions_by_channel_name(channel_name):
    '''
    Simple helper to get all the questions for a channel, searched by name.
    Mainly for the controller route to sound sane
    '''
    channel = db.session.query(app.knowledgebase.Channel).\
        filter_by(name=channel_name).first()

    if channel is not None:
        return channel.questions
    else:
        return None


def get_answer_by_id(answer_id):
    '''
    Simple helper to return any answer in the database that matches
    the id given
    '''
    return db.session.query(app.knowledgebase.Answer).get(answer_id)
