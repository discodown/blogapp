from datetime import datetime
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from . import db

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body =  db.Column(db.Text)
    body_html = db.Column(db.Text)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author = db.Column(db.String())
