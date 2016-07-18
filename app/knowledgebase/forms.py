from flask_security.forms import ConfirmRegisterForm, Required, Form, SubmitField
from wtforms import StringField, IntegerField
from wtforms.validators import NumberRange
from wtforms.widgets import TextArea


class ReplyForm(Form):
    reply = StringField('Reply', validators=[Required()], widget=TextArea())
    submit = SubmitField()
