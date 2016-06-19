# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import Telepot and pretty printing
import telepot
from pprint import pprint

# Jinja2 for pluralize
from jinja2_pluralize import pluralize_dj

# Auth
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required


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

# AUTH
# Start Telegram bot loop
TOKEN = '228426808:AAFjJ1Aj9PaRhlVSIIQ3sNRhxjFT_nEEd1A'


@app.route("/")
@login_required
def homepage():
    return render_template('home.html')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Before we create the database tables - import all models
from accounts import User, TelegramAccountManager, Role
from knowledgebase import Question, Answer, Vote, Comment, Channel, KBManager


# Build the database:
# This will create the database file using SQLAlchemy
db.drop_all()
db.create_all()

# create a user
TelegramAccountManager.create_account_if_does_not_exist(123, "Sriram")
TelegramAccountManager.create_account_if_does_not_exist(124, "Yew Siang")
TelegramAccountManager.create_account_if_does_not_exist(125, "Herbert")

# Seed channels
db.session.add(Channel(name='gerk1000'))
db.session.add(Channel(name='mom1000'))
db.session.add(Channel(name='pap1000'))
db.session.add(Channel(name='bro1000'))
db.session.add(Channel(name='sis1000'))

question_id = KBManager.ask_question(123, 'mom1000', "What is life?")
KBManager.add_answer_to_question(question_id, 124, "42")
KBManager.add_answer_to_question(question_id, 125, "43!")


db.session.commit()

# SECURITY/AUTH
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Import a module / component using its blueprint handler variable
from app.knowledgebase.controllers import mod_knowledgebase

# Register blueprint(s)
app.register_blueprint(mod_knowledgebase)
# app.register_blueprint(xyz_module)
# ..

# Does pluralization of words based on attached number
app.jinja_env.filters['pluralize'] = pluralize_dj

# x = User(2, 3)
# print x
# db.session.add(x)
# db.session.commit()

print "==***+**+***+*++===  WARNING - DISABLED BOT FOR TESTING **+**+*+++==="
#from telegram import bot
#bot.message_loop()
print " "
