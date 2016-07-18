from flask_security.forms import ConfirmRegisterForm, Required, Form, SubmitField
from wtforms import StringField


class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('Name', [Required()])


class OTPForm(Form):
    otp = StringField('OTP', [Required()])
    submit = SubmitField()
