import os

# Jinja2 for settings
from jinja2 import Environment
from jinja2_pluralize import pluralize_dj


class BaseConfig(object):
    PROJECT = "fbone"

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(
        os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    ADMINS = ['frizensami@gmail.com.com']

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    # hashing time - higher better
    HASH_ROUNDS = 100000

    # force SQLALCHEMY to echo
    SQLALCHEMY_ECHO = False

    # LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')
    # make_dir(LOG_FOLDER)

    # Fild upload, should override in production.
    # Limited the maximum allowed payload to 16 megabytes.
    # http://flask.pocoo.org/docs/patterns/fileuploads/#improving-uploads
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'uploads')
    # make_dir(UPLOAD_FOLDER)



    # Does pluralization initialization and checking
    env = Environment()
    env.filters['pluralize'] = pluralize_dj
    tmpl = env.from_string('vote{{ 0|pluralize }}')
    assert tmpl.render() == 'votes'


class DevelopmentConfig(BaseConfig):
    # Statement for enabling the development environment
    DEBUG = True
    PROJECT_ROOT = os.path.abspath(
        os.path.dirname(os.path.dirname(__file__)))
    # Define the database - we are working with
    # SQLite for this example
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(PROJECT_ROOT, 'app.db')
    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    CSRF_SESSION_KEY = "secret"

    # Secret key for signing cookies
    SECRET_KEY = "secret"


class TestConfiguration(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # uncomment the join part to access the test db if need be
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # \ + join(_cwd, 'testing.db')

    # Since we want our unit tests to run quickly
    # we turn this down - the hashing is still done
    # but the time-consuming part is left out.
    HASH_ROUNDS = 1
