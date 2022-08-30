import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class.

    Methods
    -------
    init_app(app)
        Run application.
    """

    SQLALCHEMY_TRACK_MODIFICATIONS = False      # Don't track database modifications to save memory
    BLOG_POSTS_PER_PAGE = 5     # Number of posts to display per pagination page
    SECRET_KEY = 'csrf'         # Key for CSRF on forms
    BLOG_ADMIN = 'admin'        # Username for blog administrator

    @staticmethod
    def init_app(app):
        """
        Empty init_app method.

        :param Flask app: The application instance.
        :return: None
        """

        pass


class DevelopmentConfig(Config):
    """
    A configuration for development.

    Extends the Config class. Sets a debug flag to True and sets database URI to
    the development database.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    """
    A configuration for testing.

    Extends the Config class. Sets a testing flag to True and sets database URI to
    the testing database.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev-test.sqlite')


class ProductionConfig(Config):
    """
    A configuration for production.

    Extends the Config class. Sets database URI to the production database.
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
