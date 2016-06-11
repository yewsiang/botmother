# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db
from app.knowledgebase import KBManager

# Define the main blueprint for this module: knowledgebase
mod_knowledgebase = Blueprint('knowledgebase', __name__, url_prefix='/knowledgebase')


@mod_knowledgebase.route('/', methods=['GET'])
def home():
    # Retrieve the last
    modules = KBManager.retrive_all_module_objects()
    return render_template('knowledgebase/home.html', modules=modules)

