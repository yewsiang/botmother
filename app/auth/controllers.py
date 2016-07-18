from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.security import login_required, current_user
from models import OTPForm
from datetime import datetime
from app.accounts import TelegramAccountManager

# Define the main blueprint for this module: knowledgebase
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


@mod_auth.route('/register_otp', methods=['GET', 'POST'])
@login_required
def home():
    form = OTPForm(request.form)

    if request.method == 'POST' and form.validate():
        otp = form.otp.data
        # Validate the OTP for the user
        if current_user.current_otp == int(otp) and current_user.otp_expiry > datetime.now():
            return ""
        else:
            return ""

    return render_template('auth/register_otp.html', form=form)
