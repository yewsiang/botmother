from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    telegram_user_id = db.Column(db.Integer)

    # questions = db.relationship('Question', backref='user', lazy='dynamic')

    # answers = db.relationship('Answer', backref='user', lazy='dynamic')

    # gameobject = db.relationship(
    #    'Gameobjects', backref='user', lazy='dynamic', uselist=False)

    user_type = db.Column(db.Integer)

    # votes = db.relationship('Vote', backref='user', lazy='dynamic')

    # channels

    def __init__(self, telegram_user_id, user_type):
        self.telegram_user_id = telegram_user_id
        self.user_type = user_type
