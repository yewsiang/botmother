from app import db
from app.helpers import user_channels_table
import datetime


class Question(db.Model):
    '''
    Question model - stores a question, the person who wrote it,
    and the channel it belongs to.
    '''

    ''' TABLE NAME '''

    __tablename__ = 'questions'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    # Not sure 5000 chars is enough for one question
    text = db.Column(db.String(5000))

    answers = db.relationship('Answer', backref='question', lazy='dynamic')

    comments = db.relationship('Comment', backref='question', lazy='dynamic')

    # integer representing what state the qn is in
    #   - waiting for answers/waiting for votes/rejected/accepted
    # 0 = waiting for answers, 1 = voting,  2 = not resolved + discussing, 3 = resolved + discussing
    state = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))

    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, text, state=0):
        '''
        This creates a new question with the initial state set to
        0 = "being asked"
        '''
        if (len(text) <= 5000):
            self.text = text
            self.state = 0
        else:
            raise ValueError('Size of question > database 5000 char limit!')


class Answer(db.Model):
    '''
    Answer model - stores an answer, the votes it has received, the person
    who wrote it, and the question it is responding to.
    '''

    ''' TABLE NAME '''

    __tablename__ = 'answers'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    # Not sure 5000 chars is enough for one answer
    text = db.Column(db.String(5000))

    votes = db.relationship('Vote', backref='answer', lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    def __init__(self, text):
        if len(text) <= 5000:
            self.text = text
        else:
            raise ValueError('Answer is too long for database (<= 5000 chars)')


class Vote(db.Model):
    '''
    Vote model - stores a vote amount, who voted, and either the answer it
    was voting on or the comment is was voting on
    '''

    ''' TABLE NAME '''

    __tablename__ = 'votes'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    # Could be negative vote! Take note
    amount = db.Column(db.Integer)

    # who is the voter?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))


class Comment(db.Model):
    '''
    Comment model - stores the id of the user that commented, the question
    it is commenting on, its parent comment, and the cmment itself
    '''

    ''' TABLE NAME '''

    __tablename__ = 'comments'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    # enough characters?
    text = db.Column(db.String(5000))

    # who is the commenter?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    # we need to define a adjacent-list relationship as described
    # in the sqlalchemy docs
    # we have one parent and many children comments
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    children = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]))



class Channel(db.Model):
    '''
    Channel model - stores users that belong to it, the channel name,
    and the questions that belong to the channel.
    '''

    ''' TABLE NAME '''

    __tablename__ = 'channels'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    # 500 characters limited channel
    name = db.Column(db.String(500))

    questions = db.relationship('Question', backref='channel', lazy='dynamic')

    users = db.relationship(
        'User', secondary=user_channels_table, back_populates="channels")

    # Lowercases any module name - compat with yew siang's tolower of messages
    def __init__(self, **kwargs):
        if (kwargs['name'] is not None):
            self.name = kwargs['name'].lower()

    def __repr__(self):
        return str(self.name)
