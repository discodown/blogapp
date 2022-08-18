from flask import render_template, redirect, request, url_for, flash
from ..models import User
from .forms import LoginForm
from . import auth
from flask_login import login_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
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
        print('Invalid')
        print(form.validate_on_submit())
    print(form.validate_on_submit())

    return render_template('auth/login.html', form=form)