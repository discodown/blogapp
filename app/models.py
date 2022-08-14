from datetime import datetime
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from . import db

post_tags = db.Table('post_tags',
            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
            db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body =  db.Column(db.Text)
    body_html = db.Column(db.Text)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author = db.Column(db.String())
    tags = db.relationship('Tag', secondary=post_tags,
            backref=db.backref('posts', lazy='dynamic'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

    def __repr__(self):
        return '<Tag %s>' % self.name