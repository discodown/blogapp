from . import main
from .. import db
from ..models import Post
from flask import render_template, request, session, current_app

@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    tags = post.get_tags()
    return render_template('post.html', post=post, tags=tags)
