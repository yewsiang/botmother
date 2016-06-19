from app import db
from app.helpers import user_channels_table, get_user_by_id
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required


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

    name = db.Column(db.String(5000))

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

    '''
    Flask-Security Part
    '''

   # Define models
    roles_users = db.Table('roles_users',
                           db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, telegram_user_id, user_type):
        self.telegram_user_id = telegram_user_id
        self.user_type = user_type

    def __repr__(self):
        return str(self.telegram_user_id)

'''
    @login_manager.user_loader
    def user_loader(db_id):
        return get_user_by_id(int(db_id))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
'''


class Role(db.Model, RoleMixin):
    '''
    Defines user roles in the system (for Flask-Security)
    '''

    ''' TABLE NAME '''

    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
