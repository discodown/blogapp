from . import main
from .. import db
from ..models import *
from flask import render_template, request, session, current_app

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    recent = posts[0:5]
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)
    return render_template('index.html', posts=posts, pagination=pagination, sidebar_tags=sidebar_tags, recent=recent)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    recent=Post.query.order_by(Post.time.desc())[0:5]
    post_tags = post.get_tags()
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)
    return render_template('post.html', post=post, post_tags=post_tags, sidebar_tags=sidebar_tags, recent=recent)

@main.route('/tagged/<tag>', methods=['GET', 'POST'])
def tagged(tag):
    #Might need to ensure they are sorted by date?
    tagged = Tag.query.get(tag).get_posts()
    page = request.args.get('page', 1, type=int)

    pagination = tagged.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    recent=Post.query.order_by(Post.time.desc())[0:5]
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)
    return render_template('tagged.html', posts=posts, pagination=pagination, sidebar_tags=sidebar_tags, recent=recent, tag=tag, page=page)

