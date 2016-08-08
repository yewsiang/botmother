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
TOKEN = '228426808:AAGPfHX6yyhFdzWZeoAlNgns7sC_inAL92k'


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


def tally_votes(votes):
    # Sums all votes by their amount
    return sum(map(lambda vote: vote.amount, votes))

app.jinja_env.globals.update(tally_votes=tally_votes)
'''
# Build the database:
# This will create the database file using SQLAlchemy
db.drop_all()
db.create_all()

# create a user
# TelegramAccountManager.create_account_if_does_not_exist(123, "Sriram")
# TelegramAccountManager.create_account_if_does_not_exist(124, "Yew Siang")
# TelegramAccountManager.create_account_if_does_not_exist(125, "Herbert")

# Seed channels & faculties
fac1 = Faculty(name="SCIENCE")
POKE1000 = Channel(name='POKE1000')
LSM1303 = Channel(name='LSM1303')
CM1111 = Channel(name='CM1111')
PC1142 = Channel(name='PC1142')
fac1.channels.append(POKE1000)
fac1.channels.append(LSM1303)
fac1.channels.append(CM1111)
fac1.channels.append(PC1142)

fac2 = Faculty(name="COMPUTING")
POKE1001 = Channel(name='POKE1001')
CS1010 = Channel(name='CS1010')
CS1101S = Channel(name='CS1101S')
fac2.channels.append(POKE1001)
fac2.channels.append(CS1010)
fac2.channels.append(CS1101S)

fac3 = Faculty(name="ENGINEERING")
POKE1002 = Channel(name='POKE1002')
MA1505 = Channel(name='MA1505')
fac3.channels.append(POKE1002)
fac3.channels.append(MA1505)

fac4 = Faculty(name="FASS")
POKE1003 = Channel(name='POKE1003')
PL1101E = Channel(name='PL1101E')
fac4.channels.append(POKE1003)
fac4.channels.append(PL1101E)

fac5 = Faculty(name="BUSINESS")
POKE1004 = Channel(name='POKE1004')
ACC1002 = Channel(name='ACC1002')
fac5.channels.append(POKE1004)
fac5.channels.append(ACC1002)

fac6 = Faculty(name="LAW")
POKE1005 = Channel(name='POKE1005')
LC1003 = Channel(name='LC1003')
fac6.channels.append(POKE1005)
fac6.channels.append(LC1003)

fac7 = Faculty(name="SDE")
POKE1006 = Channel(name='POKE1006')
AR1101 = Channel(name='AR1101')
fac7.channels.append(POKE1006)
fac7.channels.append(AR1101)

fac8 = Faculty(name="MEDICINE")
POKE1007 = Channel(name='POKE1007')
MD1120 = Channel(name='MD1120')
fac8.channels.append(POKE1007)
fac8.channels.append(MD1120)

fac9 = Faculty(name="OTHERS")
POKE1008 = Channel(name='POKE1008')
UTC1102B = Channel(name='UTC1102B')
UTC1102C = Channel(name='UTC1102C')
UTC1102G = Channel(name='UTC1102G')
UTC1102H = Channel(name='UTC1102H')
UTC1102N = Channel(name='UTC1102N')
UTC1102S = Channel(name='UTC1102S')
fac9.channels.append(POKE1008)
fac9.channels.append(UTC1102B)
fac9.channels.append(UTC1102C)
fac9.channels.append(UTC1102G)
fac9.channels.append(UTC1102H)
fac9.channels.append(UTC1102N)
fac9.channels.append(UTC1102S)

db.session.add(fac1)
db.session.add(fac2)
db.session.add(fac3)
db.session.add(fac4)
db.session.add(fac5)
db.session.add(fac6)
db.session.add(fac7)
db.session.add(fac8)
db.session.add(fac9)

db.session.add(POKE1000)
db.session.add(LSM1303)
db.session.add(CM1111)
db.session.add(PC1142)

db.session.add(POKE1001)
db.session.add(CS1010)
db.session.add(CS1101S)

db.session.add(POKE1002)
db.session.add(MA1505)

db.session.add(POKE1003)
db.session.add(PL1101E)

db.session.add(POKE1004)
db.session.add(ACC1002)

db.session.add(POKE1005)
db.session.add(LC1003)

db.session.add(POKE1006)
db.session.add(AR1101)

db.session.add(POKE1007)
db.session.add(MD1120)

db.session.add(POKE1008)
db.session.add(UTC1102B)
db.session.add(UTC1102C)
db.session.add(UTC1102G)
db.session.add(UTC1102H)
db.session.add(UTC1102N)
db.session.add(UTC1102S)

# question_id = KBManager.ask_question(123, 'bobo1000', "What is life?")
# KBManager.add_answer_to_question(question_id, 124, "42")
# KBManager.add_answer_to_question(question_id, 125, "43!")
db.session.commit()
'''

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
