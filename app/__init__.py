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
LSM1102 = Channel(name='LSM1102')
CM1111 = Channel(name='CM1111')
PC1142 = Channel(name='PC1142')
fac1.channels.append(POKE1000)
fac1.channels.append(LSM1102)
fac1.channels.append(CM1111)
fac1.channels.append(PC1142)

fac2 = Faculty(name="COMPUTING")
POKE1001 = Channel(name='POKE1001')
CS1010 = Channel(name='CS1010')
CS1010S = Channel(name='CS1010S')
CS1101S = Channel(name='CS1101S')
CS1231 = Channel(name='CS1231')
fac2.channels.append(POKE1001)
fac2.channels.append(CS1010)
fac2.channels.append(CS1010S)
fac2.channels.append(CS1101S)
fac2.channels.append(CS1231)

fac3 = Faculty(name="ENGINEERING")
POKE1002 = Channel(name='POKE1002')
MA1505 = Channel(name='MA1505')
MA1506 = Channel(name='MA1506') 
EG1108 = Channel(name='EG1108')
PC1431 = Channel(name='PC1431')
PC1432 = Channel(name='PC1432')
fac3.channels.append(POKE1002)
fac3.channels.append(MA1505)
fac3.channels.append(MA1506)
fac3.channels.append(EG1108)
fac3.channels.append(PC1431)
fac3.channels.append(PC1432)

fac4 = Faculty(name="FASS")
POKE1003 = Channel(name='POKE1003')
FAS1101 = Channel(name='FAS1101')
FAS1102 = Channel(name='FAS1102')
PL1101E = Channel(name='PL1101E')
EC1101E = Channel(name='EC1101E')
GL1101E = Channel(name='GL1101E')
PS1101E = Channel(name='PS1101E')
EL1101E = Channel(name='EL1101E')
HY1101E = Channel(name='HY1101E')
SE1101E = Channel(name='SE1101E')
NM1101E = Channel(name='NM1101E')
SC1101E = Channel(name='SC1101E')
fac4.channels.append(POKE1003)
fac4.channels.append(FAS1101)
fac4.channels.append(FAS1102)
fac4.channels.append(PL1101E)
fac4.channels.append(EC1101E)
fac4.channels.append(GL1101E)
fac4.channels.append(PS1101E)
fac4.channels.append(EL1101E)
fac4.channels.append(HY1101E)
fac4.channels.append(SE1101E)
fac4.channels.append(NM1101E)
fac4.channels.append(SC1101E)

fac5 = Faculty(name="BUSINESS")
POKE1004 = Channel(name='POKE1004')
ACC1002 = Channel(name='ACC1002')
MKT1003 = Channel(name='MKT1003')
BSP1004 = Channel(name='BSP1004')
BSP1005 = Channel(name='BSP1005')
DSC1007 = Channel(name='DSC1007')
DSC2008 = Channel(name='DSC2008')
ES2002  = Channel(name='ES2002 ')

fac5.channels.append(POKE1004)
fac5.channels.append(ACC1002)
fac5.channels.append(MKT1003)
fac5.channels.append(BSP1004)
fac5.channels.append(BSP1005)
fac5.channels.append(DSC1007)
fac5.channels.append(DSC2008)
fac5.channels.append(ES2002)


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

fac9 = Faculty(name="TEMBUSU")
POKE1008 = Channel(name='POKE1008')
GER1000  = Channel(name='GER1000')
UTC1102B = Channel(name='UTC1102B')
UTC1102C = Channel(name='UTC1102C')
UTC1102G = Channel(name='UTC1102G')
UTC1102H = Channel(name='UTC1102H')
UTC1102N = Channel(name='UTC1102N')
UTC1102S = Channel(name='UTC1102S')
UTW1001K = Channel(name='UTW1001K')
UTW1001M = Channel(name='UTW1001M')
UTW1001N = Channel(name='UTW1001N')
UTW1001P = Channel(name='UTW1001P')
UTW1001R = Channel(name='UTW1001R')
UTW1001V = Channel(name='UTW1001V')
UTW1001W = Channel(name='UTW1001W')
UTW2001H = Channel(name='UTW2001H')
UTW2001J = Channel(name='UTW2001J')
UTW2001Q = Channel(name='UTW2001Q')
UTW2001S = Channel(name='UTW2001S')
UTW2001T = Channel(name='UTW2001T')
UTC2105  = Channel(name='UTC2105')
UTC2107  = Channel(name='UTC2107')
UTS2100  = Channel(name='UTS2100')
fac9.channels.append(POKE1008)
fac9.channels.append(GER1000)
fac9.channels.append(UTC1102B)
fac9.channels.append(UTC1102C)
fac9.channels.append(UTC1102G)
fac9.channels.append(UTC1102H)
fac9.channels.append(UTC1102N)
fac9.channels.append(UTC1102S)
fac9.channels.append(UTW1001K)
fac9.channels.append(UTW1001M)
fac9.channels.append(UTW1001N)
fac9.channels.append(UTW1001P)
fac9.channels.append(UTW1001R)
fac9.channels.append(UTW1001V)
fac9.channels.append(UTW1001W)
fac9.channels.append(UTW2001H)
fac9.channels.append(UTW2001J)
fac9.channels.append(UTW2001Q)
fac9.channels.append(UTW2001S)
fac9.channels.append(UTW2001T)
fac9.channels.append(UTC2105)
fac9.channels.append(UTC2107)
fac9.channels.append(UTS2100)

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
db.session.add(LSM1102)
db.session.add(CM1111)
db.session.add(PC1142)

db.session.add(POKE1001)
db.session.add(CS1010)
db.session.add(CS1010S)
db.session.add(CS1101S)
db.session.add(CS1231)

db.session.add(POKE1002)
db.session.add(MA1505)
db.session.add(MA1506)
db.session.add(EG1108)
db.session.add(PC1431)
db.session.add(PC1432)

db.session.add(POKE1003)
db.session.add(PL1101E)
db.session.add(POKE1003)
db.session.add(FAS1101)
db.session.add(FAS1102)
db.session.add(EC1101E)
db.session.add(GL1101E)
db.session.add(PS1101E)
db.session.add(EL1101E)
db.session.add(HY1101E)
db.session.add(SE1101E)
db.session.add(NM1101E)
db.session.add(SC1101E)

db.session.add(POKE1004)
db.session.add(ACC1002)
db.session.add(MKT1003)
db.session.add(BSP1004)
db.session.add(BSP1005)
db.session.add(DSC1007)
db.session.add(DSC2008)
db.session.add(ES2002 )

db.session.add(POKE1005)
db.session.add(LC1003)

db.session.add(POKE1006)
db.session.add(AR1101)

db.session.add(POKE1007)
db.session.add(MD1120)

db.session.add(POKE1008)
db.session.add(GER1000)
db.session.add(UTC1102B)
db.session.add(UTC1102C)
db.session.add(UTC1102G)
db.session.add(UTC1102H)
db.session.add(UTC1102N)
db.session.add(UTC1102S)
db.session.add(UTW1001K)
db.session.add(UTW1001M)
db.session.add(UTW1001N)
db.session.add(UTW1001P)
db.session.add(UTW1001R)
db.session.add(UTW1001V)
db.session.add(UTW1001W)
db.session.add(UTW2001H)
db.session.add(UTW2001J)
db.session.add(UTW2001Q)
db.session.add(UTW2001S)
db.session.add(UTW2001T)
db.session.add(UTC2105)
db.session.add(UTC2107)
db.session.add(UTS2100)

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
