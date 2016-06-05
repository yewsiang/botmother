from app import db
from app.helpers import user_channels_table


class User(db.Model):
    '''
    Refers to a complex user that could come from telegram or the web
    interface or both together. Provides authentication for the web
    and saving of points/questions/answers to the DB.
    '''

    ''' TABLE NAME '''

    __tablename__ = 'users'

    ''' ATTRIBUTES '''

    id = db.Column(db.Integer, primary_key=True)

    telegram_user_id = db.Column(db.Integer, unique=True)

    questions = db.relationship('Question', backref='user', lazy='dynamic')

    answers = db.relationship('Answer', backref='user', lazy='dynamic')

    # gameobject = db.relationship(
    #     'Gameobjects', backref='user', lazy='dynamic', uselist=False)

    user_type = db.Column(db.Integer)

    votes = db.relationship('Vote', backref='user', lazy='dynamic')

    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    channels = db.relationship(
        'Channel', secondary=user_channels_table, back_populates="users")

    def __init__(self, telegram_user_id, user_type):
        self.telegram_user_id = telegram_user_id
        self.user_type = user_type

    def __repr__(self):
        return str(self.telegram_user_id)
