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

