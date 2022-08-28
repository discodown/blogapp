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
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)

    if app.config['TESTING']:

        def time_filter(time, format="%B %-d, %Y at %-I:%M %p"):
            return time.strftime(format)
        app.jinja_env.filters['time'] = time_filter

        def text_preview(text):
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