"""
Application package constructor.

Methods
-------
create_app(config_name)
    Application factory function.
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_ckeditor import CKEditor
from flask_login import LoginManager
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
ckeditor = CKEditor()
db = SQLAlchemy()

def create_app(config_name):
    """
    Application factory function to launch the application by creating the application instance.

    The application is configured based on the configuration name passed to the
    method when it is called. All Flask extensions instances created earlier are
    initialized. If the app is created for testing purposes,  Jinja environment variables
    must be set in order to access filters without running the blog.py script.

    :param str config_name: The configuration to use when creating the app.
    :return Flask app: The Flask application instance.
    """

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)

    # Filters need to be set as Jinja environment variables to be used during testing
    if app.config['TESTING']:

        def time_filter(time, format="%B %-d, %Y at %-I:%M %p"):
            """
            Format a DateTime object to display a post's time of creation in nicer format.

            :param DateTime time: A DataTime object from a post's time attribute.
            :param str format: A formatting string for a date and time.
            :return str: The post's date and time of creation, formatted.
            """

            return time.strftime(format)
        app.jinja_env.filters['time'] = time_filter

        def text_preview(text):
            """
            Create a preview of a post's body.

            Outside of the post's permalink page, only the first 2000 characters should be
            displayed. If a post is shorter than 2000 characters, then the entire post can be returned.
            :param str text: The entire body of a post.
            :return str: The first 2000 characters of a post, plus an ellipses to indicate continuation
            """
            if len(text) < 2000:
                return text
            else:
                return text[0:2000] + '...'
        app.jinja_env.filters['preview'] = text_preview

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app