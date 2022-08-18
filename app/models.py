from datetime import datetime
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

post_tags = db.Table('post_tags',
            db.Column('tag_id', db.String(), db.ForeignKey('tag.name')),
            db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body =  db.Column(db.UnicodeText)
    body_html = db.Column(db.Text)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author = db.Column(db.String(), default="Anonymous Blogger")
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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('Password is non-readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r' % self.name