from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.security import login_required, current_user, login_user, logout_user
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
        otp = int(form.otp.data)
        if current_user.telegram_user_id <= 0:
            merged_user = TelegramAccountManager.merge_accounts_through_otp(current_user, otp)

            if merged_user is not None:
                # success state
                print "Success!"
                logout_user()
                login_user(merged_user)
                flash('Successfully registered OTP!', 'success')
            else:
                # failure state
                print "Failure :("
                flash('Failed to register OTP!', 'error')
        else:
            print current_user.telegram_user_id
            print "User is already merged!"
            flash('You have already merged with your Telegram account :)')

    return render_template('auth/register_otp.html', form=form)
