from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from ..models import Post, Tag, Permission

@main.app_context_processor
def inject_globals():
    def recent():
        return Post.query.order_by(Post.time.desc())[0:5]

    def sidebar_tags():
        return sorted(Tag.query.all(), key=lambda tag: tag.name)

    return {'recent' : recent, 'sidebar_tags' : sidebar_tags}

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

