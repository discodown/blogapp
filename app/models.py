from datetime import datetime
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table to relate tags to posts.
post_tags = db.Table('post_tags',
                     db.Column('tag_id', db.String(), db.ForeignKey('tag.name')),
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                     )


class Post(db.Model):
    """
    Represents a blog post and the Post database table.

    Extends the Model class from flask-sqlalchemy. Each instance of Post will store
    information about a blog post as an entry in the Post table. Has a many-t-many
    relationship with Tag, represented by the post_tags association table.

    Attributes
    ----------
    __tablename__ : str
        the name of the Post table in the database schema.
    id : Column(int)
        the primary key for the table, assigned automatically.
    title : Column(str)
        the title of the blog post.
    body : Column(UnicodeText)
        the formatted body of the blog post, stored as unicode.
    body_html : Column(Text)
        the body of the test after the HTML is cleaned for security.
    time : Column(DateTime)
        the time and date that the post was created.
    author : Column(String)
        the author of the blog post.
    tags : relationship
        a list of the post's tags, represented as a many-to-many relationship via the post_tags table

    Methods
    -------
    tag(tag)
        Add a tag to a post.
    on_changed_body(target, value, oldvalue, initiator)
        Sanitize a post's body before storing it in the database.

    """

    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body = db.Column(db.UnicodeText)
    body_html = db.Column(db.Text)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author = db.Column(db.String(), default="Anonymous Blogger")
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """
        Sanitize rich text in a post's body before storing it in the database.

        Only HTML tags in allowed_tags will be permitted; all others will be removed by bleach.clean.
        The allowed tags are all HTML tags used by CKEditior's available formatting options;
        all other HTML tags will be removed.
        The cleaned HTML will be stored in the posts' body_html column whenever the body
        of the post is changed by registering this method as an event listener of
        SQLALchemy's 'set' event for the Post's body field.

        :param target: The target post.
        :param value: The target post's body, which will be cleaned.
        :param oldvalue:
        :param initiator:
        :return: None
        """

        # Permitted HTML tags
        allowed_tags = ['a', 'em', 'strong', 'h1', 'h2', 'h3,', 'pre',
                        'table', 'tbody', 'tr', 'td', 'img', 'anchor',
                        'li', 'ol', 'ul', 'p', 'blockquote', 's',
                        'cite', 'span', 'div', 'big', 'samp', 'kbd',
                        'q', 'ins', 'del', 'tt', 'small', 'var']
        # Strip all other HTML tags from the body
        target.body_html = bleach.clean(value, tags=allowed_tags, strip=True)

    def tag(self, tag):
        """
        Add a tag to a post by appending it to a post's list of tags. If necessary,
        create new Tag object and add it to the Tag database. If the tag already
        exists, query the Tag database and append the returned Tag to the post's
        list of tags.

        :param str tag: The name of the tag to be added.
        :return: None
        """
        # If a post is created without tags, assign it the "uncategorized" tag
        if tag == '':
            if Tag.query.get("uncategorized") is None:
                t = Tag(name="uncategorized")
                self.tags.append(t)
                db.session.add(t)
            else:
                self.tags.append(Tag.query.get("uncategorized"))
        else:
            if Tag.query.get(tag) is None:
                t = Tag(name=tag)
                self.tags.append(t)
                db.session.add(t)
            else:
                self.tags.append(Tag.query.get(tag))

    def get_tags(self):
        """
        Get the post's tags.
        :return List(Tag) self.tags: The post's list of Tags.
        """
        return self.tags

# Register on_changed_body as an event listener
db.event.listen(Post.body, 'set', Post.on_changed_body)

class Tag(db.Model):
    """
    Represents a post tag and the Tag database table.

    Extends the Model class from flask-sqlalchemy. Each instance of Tag will store
    information about a tag as an entry in the Tag table. Has a many-to-many
    relationship with Post, represented by the post_tags association table.


    Attributes
    ----------
    name : Column(String)
        The name of the tag and primary key of the Tag table, specified when creating a Tag.

    Methods
    -------
    ___repr___
        String representation of a Tag.
    get_posts
        Get a list of posts associated with a tag.
    """
    name = db.Column(db.String(), primary_key=True)

    def __repr__(self):
        """
        String representation of a tag.
        :return str: A string representation of a tag based on its name.
        """
        return '<Tag %s>' % self.name

    def get_posts(self):
        """
        Retrieve posts with a given tag.

        A query of the Post table is made using a join operation with the post_tags table on
        the post ID column. The query is filtered for entries in the post_tags table where
        the tag_id column matches the name of the Tag instance calling the method.

        :return BaseQuery: A query object referencing all posts in the Tag database associated with a tag.
        """
        return Post.query.join(post_tags, post_tags.c.post_id == Post.id).filter(post_tags.c.tag_id == self.name)


class User(UserMixin, db.Model):
    """
    Represents a user and the User database table.

    Each instance of Tag will store information about a user as an entry in the User table.
    Has a one-to-many relationship with Role, represented the role_id column which
    uses the primary key of Role (id) as a foreign key.

    Attributes
    ----------
    __tablename__ : str
        The name of the User table in the database schema.
    id : Column(Integer)
        The primary key of the User table, assigned automatically when a user is added to the database.
    name : Column(String)
        The name of the user, assigned when creating a User instance.
    username : Column(String)
        The username of the user, assigned when creating a User instance. Must be unique.
    password_hash : Column(String)
        A hash of the user's password, generated from the password given when creating a User instance.
    role_id : Column(Integer)
        Integer representing the user's assigned role. References the primary key in the Role table.

    Methods
    -------
    can(perm)
        Checks whether a user has a given permission.
    is_admin()
        Checks whether a user has the Administrator role.
    password(password)
        Generate a hash from a user's password.
    verify_password(password)
        Check the hash of the given plaintext password against a user's password hash.
    __repr__
        Return a string representation of a User instance.

    Properties
    ----------
    password
        The user's non-hashed password. Read only.
    """

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        """
        Create a new User instance.

        Calls the constructor of the UserMixin class first.
        If the username matches the administrator username defined in the config file,
        the user is assigned the Administrator role. Otherwise, if no role is specified when
        the instance is created, the user is assigned the default role (defined in the Role class).

        :param kwargs:
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username == current_app.config['BLOG_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        """
        Check whether a user has a given permission.

        To pass the check, a user must first have an assigned role. Then said
        role must have the given permission.

        :param Permission perm: The permission to check.
        :return bool: True if the user has a role assigned and said role has the given permission.
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        """
        Check whether a user is an administrator.

        Calls the user instance's can() method with the ADMIN permission to
        check whether the user has said permission.

        :return bool: True if the user has the ADMIN permission.
        """
        return self.can(Permission.ADMIN)

    @property
    def password(self):
        """
        The user's non-hashed password.

        Read only after it is given when creating a User instance. If the password is accessed,
        raise an AttributeError.

        :raises AttributeError: If an attempt to read the password field is made.
        """
        raise AttributeError('Password is non-readable')

    @password.setter
    def password(self, password):
        """
        Generate a hash for the user's password.

        Called automatically when a user is assigned a password during the creation of a User instance.
        The werkzeug generate_password_hash() method is used to generate a unique hash which is stored
        in the password_hash column of a user's entry in the User table.

        :param str password: The user's unhashed password.
        :return: None
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check the hash of the given plaintext password against a user's password hash.

        Calls the werkzeug check_password_hash() method to compare the plaintext password's
        hash to the hash stored in the password_hash column of the calling User instance's
        entry in the User table.

        :param str password: A plaintext password to compare to the password hash.
        :return bool: True if the hash of the plaintext password matches the hash in the database.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        Return a string representation of a User instance.
        :return str: a string representation of a User instance.
        """
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    """
    The user loader method used by the login manager.

    Query the User table for a user with the given user ID. Convert the ID to an int
    before making the query since it is stored as an Integer in the User table's id
    column.

    :param str user_id: The ID of a user.
    :return User: The User object with the given user ID. None if no user has said ID.
    """

    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """
    A class for an anonymous (i.e. non-logged in) user.

    Extends the AnonymousUserMixin class from the flask_login module.
    Implements the User class's can and is_admin methods, which will always
    return False in this case.

    Methods
    -------
    can(permissions)
        Check whether an anonymous user has a set of permissions.
    is_admin()
        Check whether an anonymous user is an administrator.
    """

    def can(self, permissions):
        """
        Check whether an anonymous user has a set of permissions.

        Will always return false for any set of permissions; non-logged in users
        have no permissions.

        :param Permission permissions: A Permission or set of Permissions
        :return bool: False in every case.
        """
        return False

    def is_admin(self):
        """
        Check whether an anonymous user is an administrator.

        Will always return false; a non-logged in user will never have admin privileges.
        :return bool: False in every case.
        """
        return False


# Assign the AnonymousUser class to the login manager's anonymous user property.
login_manager.anonymous_user = AnonymousUser


class Permission:
    """
    An enumeration for user permissions (or privileges).

    WRITE permission allows users to create and edit blog posts.
    ADMIN permission gives a user all preceding privileges and allows them to
    make changes blog's settings (to be implemented later).

    More permissions can be added to accommodate more blog features.
    All permissions should be powers of 2 to make permission checking faster.
    """

    WRITE = 1   # Permission to create and edit posts
    ADMIN = 2   # Grants administrator privileges


class Role(db.Model):
    """
    Represents a user's role and the Role database table.

    Each instance of Role will store information about a role as an entry in the Role table.
    Has a one-to-many relationship with Role, represented by users column which is a list
    of users with a role.

    Attributes
    ----------
    ___tablename__ : str
        The name of the Role table in the database schema.
    id : Column(Integer)
        The primary key in the Role data.
    name : Column(String)
        The name of the role; must be unique.
    users: Relationship
        A list of user's assigned a role.
    default : Column(Boolean)
        Used to set the default role for a user. False by default.
    permissions: Column(Integer)
        Represents the permissions given to a user with the role.

    Methods
    -------
    __repr__
        Return a string representation of a Role instance.
    add_permission(perm)
        Add a Permission to a role's granted permissions.
    remove_permission(perm)
        Remove a Permission from a role's granted permissions.
    reset_permission()
        Remove all permissions from a Role's granted permissions.
    has_permission(perm)
        Check whether a role has a given permission.
    insert_roles()
        Initialize all roles and add them to the database.
    """

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):
        """
        Return a string representation of a Role instance.
        :return str: a string representation of a Role instance.
        """
        return '<Role %r>' % self.name

    def add_permission(self, perm):
        """
        Add a Permission to a role's granted permissions.

        Adds the numerical value of a permission to a role's permissions column
        in its entry in the Role table. Only done if the role does not already
        have the permission.

        :param Permission perm: A permission to add to a role's permissions.
        :return: None
        """
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """
        Remove a Permission from a role's granted permissions.

        Removes the numerical value of a permission to a role's permissions column
        in its entry in the Role table. Only done if the role already has the permission.
        :param Permission perm: A permission to remove from the role's permissions.
        :return: None
        """

        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """
        Remove all permissions from a Role's granted permissions.

        Resets permissions by setting the value of the role's permissions column in
        the Role table to 0.
        :return: None
        """

        self.permissions = 0

    def has_permission(self, perm):
        """
        Check whether a role has a given permission.

        Performs a bitwise and on the role's permissions attribute with the given permission.
        Since all permissions are powers of 2, the bitwise and should return the given permission's
        numerical value.

        :return bool: True is the role has the given permission.
        """
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        """
        Initialize all roles and add them to the database.

        All possible roles and their permissions are defined in the roles dictionary.
        The default role, assigned to a user when no role is specified when creating
        a User instance, is set to the Guest role.

        The Role table is queried for each role in roles. If no entry is found, a Role instance
        is created for the role. Each permission associated with the role in roles is then
        added to the new Role's permissions. If the role is the default role, its default
        attribute is set to True. Finally, the role is added to the database.

        This static method is only meant to be called when creating the database during deployment
        or testing.
        :return: None
        """

        roles = {
            'Guest': [Permission.WRITE],
            'Administrator': [Permission.WRITE, Permission.ADMIN]
        }

        default_role = 'Guest'

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
