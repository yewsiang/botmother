# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.security import current_user, login_required
import flask
# Import the database object from the main app module
from app import db
from app.knowledgebase import KBManager, Question, Answer, Vote
from app.helpers import get_all_questions_by_channel_name, get_question_by_id
from app.knowledgebase.forms import ReplyForm

# Get json to convert objects to JS output
import json

# Flask exceptions
from werkzeug.exceptions import NotFound

# Define the main blueprint for this module: knowledgebase
mod_knowledgebase = Blueprint(
    'knowledgebase', __name__, url_prefix='/knowledgebase')


@mod_knowledgebase.route('/', methods=['GET'])
def home():
    # Retrieve the last
    faculties = KBManager.retrieve_all_faculties()
    modules = KBManager.retrive_all_module_objects()

    # Convert the modules to search content
    search_content = []

    # Loop through all the modules and add them to the semantic search bar
    for module in modules:
        search_content.append({'title': module.name.upper(),
                               'url': url_for('knowledgebase.channel', channel_name=module.name)})


    # convert to json
    search_content = json.dumps(search_content)
    return render_template('knowledgebase/home.html', faculties=faculties, search_content=search_content)


@mod_knowledgebase.route('/<string:faculty_name>', methods=['GET'])
def faculty(faculty_name):
    modules = KBManager.retrieve_all_modules_from_faculty(faculty_name)
    if modules is not None:
        return render_template('knowledgebase/faculty.html', modules=modules, faculty_name=faculty_name)
    else:
        raise NotFound()


@mod_knowledgebase.route('/modules/<string:channel_name>', methods=['GET'])
def channel(channel_name):
    questions = get_all_questions_by_channel_name(channel_name)
    if questions is not None:
        return render_template('knowledgebase/channel.html', questions=questions, channel_name=channel_name)
    else:
        raise NotFound()


@mod_knowledgebase.route('/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    form = ReplyForm(request.form)
    question = get_question_by_id(question_id)
    answers = question.answers

    if request.method == 'POST' and form.validate() and current_user.is_authenticated:
        # Do something with the form info if the current user is good to go
        # and the input is sensible
        KBManager.add_answer_to_question(question_id, current_user.telegram_user_id, form.reply.data)
        flash('Answer added!', 'success')

    return render_template('knowledgebase/question.html', question=question, answers=answers, form=form)


@mod_knowledgebase.route('/answers/<int:answer_id>/upvote', methods=['POST'])
@login_required
def upvote(answer_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is not None:
        vote_state = KBManager.add_vote_to_answer(answer_id, current_user.telegram_user_id, 1)
        if vote_state:
            return_dict = {"answer_id": answer_id, "new_vote_state": 1}
            return flask.jsonify(**return_dict), 200
            # This means that this is the new amount
        else:
            return_dict = {"answer_id": answer_id, "new_vote_state": 0}
            return flask.jsonify(**return_dict), 200
    else:
        return flask.jsonify(**{}), 404


@mod_knowledgebase.route('/answers/<int:answer_id>/downvote', methods=['POST'])
@login_required
def downvote(answer_id):
    answer = db.session.query(Answer).get(answer_id)
    if answer is not None:
        vote_state = KBManager.add_vote_to_answer(answer_id, current_user.telegram_user_id, -1)
        if vote_state:
            return_dict = {"answer_id": answer_id, "new_vote_state": -1}
            return flask.jsonify(**return_dict), 200
            # This means that this is the new amount
        else:
            return_dict = {"answer_id": answer_id, "new_vote_state": 0}
            return flask.jsonify(**return_dict), 200
    else:
        return flask.jsonify(**{}), 404
