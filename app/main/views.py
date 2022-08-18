from . import main
from .. import db
from ..models import *
from flask import render_template, request, session, current_app, redirect
from .forms import PostForm

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

@main.route('/post/<int:id>', methods=['GET', 'POST'])
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

@main.route('/author/<author>')
def author(author):
    #Might need to ensure they are sorted by date?
    tagged = Tag.query.get(tag).get_posts()
    page = request.args.get('page', 1, type=int)

    pagination = tagged.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)

    posts = pagination.items
    recent=Post.query.order_by(Post.time.desc())[0:5]
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)
    return render_template('author.html', posts=posts, pagination=pagination, sidebar_tags=sidebar_tags, recent=recent, tag=tag, page=page)


@main.route('/new_post', methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    recent=Post.query.order_by(Post.time.desc())[0:5]
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)
    if form.validate_on_submit():
        post = Post(body = form.body.data, title=form.title.data)
        for t in form.tags.data.split(', '):
            post.tag(t)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id, recent=recent, sidebar_tags=sidebar_tags))
    return render_template('new_post.html', sidebar_tags=sidebar_tags, recent=recent, form=form)

@main.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    recent=Post.query.order_by(Post.time.desc())[0:5]
    sidebar_tags = sorted(Tag.query.all(), key=lambda tag: tag.name)

    post = Post.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        for t in form.tags.data.split(', '):
            post.tag(t)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))

    #should find a better way to get the tags
    tag_list = []
    for t in post.get_tags():
        tag_list.append(t.name)
    tags = ', '.join(tag_list).strip(',')
    form.body.data = post.body
    form.title.data = post.title
    form.tags.data = tags

    return render_template('edit.html', form=form, recent=recent, sidebar_tags=sidebar_tags)