from datetime import datetime
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from . import db

post_tags = db.Table('post_tags',
            db.Column('tag_id', db.String(), db.ForeignKey('tag.name')),
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

    def tag(self, tag):
        if Tag.query.get(tag) is None:
            t = Tag(name=tag)
            self.tags.append(t)
            db.session.add(t)
        else:
            self.tags.append(Tag.query.get(tag))

    def get_tags(self):
        return self.tags

class Tag(db.Model):
    name = db.Column(db.String(), primary_key=True)

    def __repr__(self):
        return '<Tag %s>' % self.name

    def get_posts(self):
         return Post.query.join(post_tags, post_tags.c.post_id == Post.id).filter(post_tags.c.tag_id == self.name)
