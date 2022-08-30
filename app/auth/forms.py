"""
Contains forms related to user authentication.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    """
    A form for logging a user in.

    Extends the FlaskForm class from flask_wtf. Contains fields for the username
    and password, a BooleanField representing a checkbox that will keep a user
    logged in if checked, and a submit field for submitting the login data.
    The username and password fields cannot be empty.

    Attributes
    ----------
    username : StringField(label='Username', validators=[DataRequired(), Length(1, 64)])
        A field for the username.
    password : PasswordField(label='Password', validators=[DataRequired()])
        A field for the password.
    remember_me : BooleanField(label='Keep me logged in')
        A field for a "Remember me" checkbox.
    submit : SubmitField(label='Log In')
        A submit field for submitting the login data and attempting to authenticate the user.
    """
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')