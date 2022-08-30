"""
The main blueprint. Contains views and forms related to creating and editing posts.

Methods
-------

inject_globals()
    Add global variables needed to render templates to the app context.

inject_permissions()
    Add Permissions needed to render templates to the app context.


"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from ..models import Post, Tag, Permission

@main.app_context_processor
def inject_globals():
    """
    Add global variables needed to render templates to the app context.

    The variables in this case are filters, i.e. functions that can be called from
    a Jinja template to get formatted data.

    Methods
    -------
    recent()
        Get the five most recent posts so they can be displayed in the sidebar.
    sidebar_tags()
        Get all tags in the Tag database so they can be displayed in the sidebar.

    :return dict(func): A dictionary of functions that can be called from a Jinja template.
    """

    def recent():
        """
        Get the five most recent posts so they can be displayed in the sidebar.

        The Post database is queried with results returned in descending time order.
        The first five elements from the returned list are sliced and returned
        by the function.

        :return BaseQuery: A query object containing the five most recent posts.
        """

        return Post.query.order_by(Post.time.desc())[0:5]

    def sidebar_tags():
        """
        Get all tags in the Tag database so they can be displayed in the sidebar.

        The Tag database is queried for all entries and a list is created from the tags'
        names.
        :return list(str): A list of all tag names.
        """

        return sorted(Tag.query.all(), key=lambda tag: tag.name)

    return {'recent' : recent, 'sidebar_tags' : sidebar_tags}

@main.app_context_processor
def inject_permissions():
    """
    Add Permissions needed to render templates to the app context.

    This function simply makes the Permission class from app.models accessible
    from a template. This is necessary to check a user's permissions from a template
    when deciding whether to display an element on the page.

    :return dict(Permission): A dictionary of all permissions from app.models.Permission
    """

    return dict(Permission=Permission)

