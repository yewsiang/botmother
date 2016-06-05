# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import Telepot and pretty printing
import telepot
from pprint import pprint

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config.DevelopmentConfig')

# to avoid circular

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

db.init_app(app)
# app.register_blueprint(accounts)

# Start Telegram bot loop
TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
# from app.mod_auth.controllers import mod_auth as auth_module

# Register blueprint(s)
# app.register_blueprint(auth_module)
# app.register_blueprint(xyz_module)
# ..

# Before we create the database tables - import all models
from accounts import User
from knowledgebase import Question, Answer, Vote, Comment, Channel


# Build the database:
# This will create the database file using SQLAlchemy
#db.drop_all()
#db.create_all()

db.session.add(Channel(name='gerk1000'))
db.session.add(Channel(name='mom1000'))
db.session.add(Channel(name='pap1000'))
db.session.add(Channel(name='bro1000'))
db.session.add(Channel(name='sis1000'))
db.session.commit()

# x = User(2, 3)
# print x
# db.session.add(x)
# db.session.commit()


from telegram import bot
bot.message_loop()
