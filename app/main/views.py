from . import main
from .. import db
from ..models import Post
from flask import render_template

@main.route('/')
def index():
    return render_template('index.html')