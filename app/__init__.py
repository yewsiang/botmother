# Import flask and template operators
from flask import Flask, render_template, url_for, redirect

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Import Telepot and pretty printing
import telepot
from pprint import pprint

# Jinja2 for pluralize
from jinja2_pluralize import pluralize_dj

# Auth
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required

# For confirmation mail sending
from flask_mail import Mail

# For a replacement register form
from app.auth import ExtendedRegisterForm


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
def homepage():
    return redirect(url_for('knowledgebase.home'))


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Functions for Jinja
# Random colors for the cards
import math, random
colors = ["red", "orange", "yellow", "olive", "green", "teal", "blue", "violet", "purple", "pink", "brown", "grey", "black"]
def random_color():
    return colors[int(math.floor(random.random() * len(colors)))]
# Find channel name to print on the page
def find_channel_name(channel_id):
    channel = db.session.query(Channel).get(channel_id)
    return channel.name.upper()
app.jinja_env.globals.update(random_color=random_color)
app.jinja_env.globals.update(find_channel_name=find_channel_name)


# Before we create the database tables - import all models
from accounts import User, TelegramAccountManager, Role
from knowledgebase import Question, Answer, Vote, Comment, Channel, KBManager, Faculty

# Build the database:
# This will create the database file using SQLAlchemy
db.drop_all()
db.create_all()

# create a user
TelegramAccountManager.create_account_if_does_not_exist(123, "Sriram")
TelegramAccountManager.create_account_if_does_not_exist(124, "Yew Siang")
TelegramAccountManager.create_account_if_does_not_exist(125, "Herbert")

# Seed channels & faculties
fac1 = Faculty(name="SCIENCE")
fac2 = Faculty(name="COMPUTING")
CS1010 = Channel(name='CS1010')
CS1020 = Channel(name='CS1020')
BOBO1000 = Channel(name='BOBO1000')
fac1.channels.append(BOBO1000)
fac2.channels.append(CS1010)
fac2.channels.append(CS1020)

db.session.add(fac1)
db.session.add(fac2)
db.session.add(CS1010)
db.session.add(CS1020)
db.session.add(BOBO1000)

question_id = KBManager.ask_question(123, 'bobo1000', "What is life?")
KBManager.add_answer_to_question(question_id, 124, "42")
KBManager.add_answer_to_question(question_id, 125, "43!")

db.session.commit()

# SECURITY/AUTH
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, confirm_register_form=ExtendedRegisterForm)
# SECURITY-MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'nusbotmother@gmail.com'
app.config['MAIL_PASSWORD'] = 'cawwR73cT2VQRkZN'
mail = Mail(app)

# Import a module / component using its blueprint handler variable
from app.knowledgebase.controllers import mod_knowledgebase
from app.auth.controllers import mod_auth

# Register blueprint(s)
app.register_blueprint(mod_knowledgebase)
app.register_blueprint(mod_auth)
# app.register_blueprint(xyz_module)
# ..

# Does pluralization of words based on attached number
app.jinja_env.filters['pluralize'] = pluralize_dj

# x = User(2, 3)
# print x
# db.session.add(x)
# db.session.commit()

from telegram import bot

bot.message_loop()
print " "
