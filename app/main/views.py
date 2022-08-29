from . import main
from .. import db
from ..models import *
from flask import render_template, request, session, current_app, redirect, abort, flash
from .forms import PostForm
from flask_login import login_required, current_user
from app.decorators import permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    post_tags = post.get_tags()
    return render_template('post.html', post=post, post_tags=post_tags)


@main.route('/tagged/<tag>', methods=['GET', 'POST'])
def tagged(tag):
    # Might need to ensure they are sorted by date?
    page = request.args.get('page', 1, type=int)
    tagged = Tag.query.get(tag).get_posts()

    pagination = tagged.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    return render_template('tagged.html', posts=posts, pagination=pagination, tag=tag)


@main.route('/author/<author>')
def author(author):
    # Might need to ensure they are sorted by date?
    posts_by = Post.query.filter_by(author=author)
    page = request.args.get('page', 1, type=int)

    ##could this be moved to a context processor?
    pagination = posts_by.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)

    posts = pagination.items
    return render_template('author.html', posts=posts, pagination=pagination, author=author, page=page)


@main.route('/new_post', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.body.data, title=form.title.data, author=current_user.name)
        for t in form.tags.data.split(', '):
            post.tag(t)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    return render_template('new_post.html', form=form)


@main.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit(id):
    # TODO: verify that logged in user is the author of the post
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

    # should find a better way to get the tags
    tag_list = []
    for t in post.get_tags():
        tag_list.append(t.name)
    tags = ', '.join(tag_list).strip(',')
    form.body.data = post.body
    form.title.data = post.title
    form.tags.data = tags

    return render_template('edit.html', form=form)


@main.route("/delete/<int:id>", methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def delete(id):
    # TODO: verify that logged in user is the author of the post
    post = Post.query.get_or_404(id)
    tags = post.get_tags()
    db.session.delete(post)
    db.session.commit()
    for tag in tags:
        print(Tag.query.get(tag.name).get_posts().first())
        if Tag.query.get(tag.name).get_posts().first() is None:
            db.session.delete(tag)
            db.session.commit()
    flash('Post successfully deleted.')

    return redirect(url_for('.index'))
