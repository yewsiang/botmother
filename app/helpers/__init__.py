from app import db

# Create the association table between channels and users
user_channels_table = db.Table('userchannels', db.Model.metadata,
                               db.Column('user_id', db.Integer,
                                         db.ForeignKey('users.id')),
                               db.Column('channel_id', db.Integer,
                                         db.ForeignKey('channels.id'))
                               )
