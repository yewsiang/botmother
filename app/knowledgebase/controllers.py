# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db
from app.knowledgebase import KBManager

# Get json to convert objects to JS output
import json

# Define the main blueprint for this module: knowledgebase
mod_knowledgebase = Blueprint('knowledgebase', __name__, url_prefix='/knowledgebase')


@mod_knowledgebase.route('/', methods=['GET'])
def home():
    # Retrieve the last
    modules = KBManager.retrive_all_module_objects()

    # Convert the modules to search content
    search_content = []

    # Loop through all the modules and add them to the semantic search bar
    for module in modules:
        search_content.append({'title': module.name.upper()})

    # convert to json
    search_content = json.dumps(search_content)
    return render_template('knowledgebase/home.html', modules=modules, search_content=search_content)

