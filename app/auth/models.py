from flask_security.forms import ConfirmRegisterForm, Required, Form, SubmitField
from wtforms import StringField, IntegerField
from wtforms.validators import NumberRange


class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('Name', [Required()])


class OTPForm(Form):
    otp = IntegerField('One-Time Password', [Required(), NumberRange(min=100000, max=999999, message="One-Time Password is invalid!")])
    submit = SubmitField()
