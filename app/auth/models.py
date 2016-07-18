from flask_security.forms import ConfirmRegisterForm, Required
from wtforms import StringField


class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('Name', [Required()])
