"""
Contains view functions for the auth blueprint, related to user authentication.

Methods
-------

login()
    Log a user in.
logout()
    Log a user out.
"""

from flask import render_template, redirect, request, url_for, flash
from ..models import User
from .forms import LoginForm
from . import auth
from flask_login import login_user, logout_user, login_required

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log a user in by attempting to authenticate them using data from the login form.

    To be submitted, the form data must pass the validation defined in
    the LoginForm class. To authenticate the user, the username data is used to
    query the User table. If a user with said username is found, the hash
    of the data in the password field is compared to the password hash stored in
    the user's database entry. If they match, the user us logged in and redirected
    to the blog homepage or to the page they attempted to access before logging in.

    If the authentication fails, the user is flashed a message and remains on the
    login page without being logged in.
    :return str: A jinja template for the login page.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    Log a user out after they have logged in.

    Requires a user to be logged in to access. Does not render a template, but
    simply calls the logout_user method from flask_login to log a user out when accessed.
    A message is flashed and the user is redirected to the blog homepage after being logged
    out.
    :return str: A redirect to the blog home page.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))