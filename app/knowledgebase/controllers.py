# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db
from app.knowledgebase import KBManager
from app.helpers import get_all_questions_by_channel_name, get_question_by_id

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
    modules = KBManager.retrive_all_module_objects()

    # Convert the modules to search content
    search_content = []

    # Loop through all the modules and add them to the semantic search bar
    for module in modules:
        search_content.append({'title': module.name.upper(),
                               'url': url_for('knowledgebase.channel', channel_name=module.name)})

    # convert to json
    search_content = json.dumps(search_content)
    return render_template('knowledgebase/home.html', modules=modules, search_content=search_content)


@mod_knowledgebase.route('/<string:channel_name>', methods=['GET'])
def channel(channel_name):
    questions = get_all_questions_by_channel_name(channel_name)
    if questions is not None:
        return render_template('knowledgebase/channel.html', questions=questions)
    else:
        raise NotFound()


@mod_knowledgebase.route('/<int:question_id>', methods=['GET'])
def question(question_id):
    question = get_question_by_id(question_id)
    answers = question.answers
    return render_template('knowledgebase/question.html', question=question, answers=answers)
