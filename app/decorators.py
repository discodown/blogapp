"""
Decorators for view functions.

These functions require a logged-in user to have certain permissions in order to
access a page by attaching restrictive decorators to the page's view functions.

Methods
-------

permission_required(perm)
    Require a permission for a page to be accessed.
admin_required(f):
    Require admin permission for a page to be accessed.
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    """
    Require a given permission for a page to be viewed.

    Wraps a view function so that it can only be called if the logged-in user
    has the given permission.

    :param Permission permission: The permission required to view a page.
    :return decorator: A decorator requiring the permission for a view function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_requited(f):
    """
    Require admin permission for a page to be accessed.

    Call the permission_required() method to create a decorator that requires
    the logged-in user to have the administrator permission for the function to
    be called.
    :param func f: A view function to be restricted to admin only.
    :return decorator:  A decorator requiring the administrator permission for a view function.
    """
    return permission_required(Permission.ADMIN)(f)