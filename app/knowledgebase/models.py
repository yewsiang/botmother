from app import db


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
    state = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))


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
    # channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))



