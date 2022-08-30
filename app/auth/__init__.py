"""
The auth blueprint. Contains views and forms related to user authentication.
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views