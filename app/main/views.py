"""
Contains all view functions for the main blueprint, which relate to blog posts.

Methods
-------
index()
    Render the blog homepage.
post(id)
    Render the permalink page of a post.
tagged(tag)
    Render a page displaying all posts with a given tag.
author(author)
    Render a page displaying all posts with a given author.
new_post()
    Render a page for creating a new post.
edit(id)
    Render a page for editing an existing post.
delete(id)
    Delete a post from the database.
"""

from . import main
from .. import db
from ..models import *
from flask import render_template, request, session, current_app, redirect, abort, flash
from .forms import PostForm
from flask_login import login_required, current_user
from app.decorators import permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    """
    Render the homepage of the blog.

    The homepage lists all blog posts, paginated and sorted from newest to oldest.
    The number of posts to display per page is set in the configuration file.

    :return str: A Jinja template for the blog homepage.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.time.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    """
    Render the permalink page of a post, with a URL created from the post ID.

    The Post table is queried using the given post ID; if no post with said ID
    is found, a 404 error is returned. The post's tags are retrieved using the post's
    get_tags() method so they can be displayed on the permalink page.

    :return str: A Jinja template for a post's permalink page.
    """

    post = Post.query.get_or_404(id)
    post_tags = post.get_tags()
    return render_template('post.html', post=post, post_tags=post_tags)


@main.route('/tagged/<tag>', methods=['GET', 'POST'])
def tagged(tag):
    """
    Render a page displaying all posts with a given tag, with a URL created from the tag name.

    To retrieve posts with the given tag, the Tag table is queried with the given
    tag name and its get_posts() method is called.

    As with the home page, posts are paginated and sorted from newest to oldest.
    :param str tag: The name of the target tag
    :return str: A Jinja template for the results page.
    """
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
    """
    Render a page displaying all posts with a given author, with a URL created from the author name.

    To retrieve posts with the given author, the Post table is queried with the author's
    name as a filter.

    As with the home page, posts are paginated and sorted from newest to oldest.

    :param str author: The name of the target author
    :return str: A Jinja template for the results page.
    """
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
    """
    Render a page for creating a new post and adding it to the database.

    The page consists of a PostForm, defined in mains.forms. To be submitted,
    the form data must pass the validation defined the the PostForm class.
    When the data is submitted, a new Post instance is created from the form data
    and added to the database. After the post is created, the user is redirected
    to the post's permalink page.

    Accessing this page requires the user to be logged in and have the WRITE permission.

    :return: A Jinja template for the new post page.
    """
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
    """
    Render a page for editing an existing post, with a URL created from the post ID.

    The page is identical to the new_post page. The only difference is that the forms
    will already be filled in with the title, body, and tags of an existing post.
    Before rendering the page, the Post database table is queried for a post with the
    given post ID. The data from that post, if it exists, is used to fill in the forms.
    After the post is updated, the user is redirected to the post's permalink page.

    Accessing this page requires the user to be logged in and have the WRITE permission.

    :param int id: The ID of the post being edited
    :return str: A Jinja template for the edit post page
    """
    # TODO: verify that logged in user is the author of the post
    post = Post.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        for t in form.tags.data.split(', '):
            # Only add new tags to a post to avoid duplicates in the post_tags table
            if t not in [tag.name for tag in post.get_tags()]:
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
    """
    Delete a post with a given post ID from the database & blog.

    Unlike the other views, delete does not render a page. It is only called from a post's
    permalink page, and redirects the user to the blog home page after deleting the post.
    If the post was the only post with a tag, that tag must also be deleted from the tag
    database. Each of the now deleted post's tags is used to query the Tag database table
    and retrieve the posts that have said tag. If no such posts are returned by the query,
    the Tag is deleted from the database.

    Accessing this page requires the user to be logged in and have the WRITE permission.

    :param int id: The ID of the post to be deleted.
    :return str: A redirect to the blog home page.
    """

    # TODO: verify that logged in user is the author of the post
    post = Post.query.get_or_404(id)
    tags = post.get_tags()
    db.session.delete(post)
    db.session.commit()
    # If necessary, delete orphaned tags after deleting the post
    for tag in tags:
        if Tag.query.get(tag.name).get_posts().first() is None:
            db.session.delete(tag)
            db.session.commit()
    flash('Post successfully deleted.')

    return redirect(url_for('.index'))
