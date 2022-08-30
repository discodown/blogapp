"""
Script for creating the blog application.

The script does the following:
    - Create the application using the application factory
    - Create in instance of the flask-migrate extension for database migration
    - Run unit tests if the application is run with the test command
    - Get coverage is the test command is run with the --coverage argument
    - Register Jinja template filters
    - Create the application's shell context

    Methods
    -------
    make_shell_context()
        Create the application's shell context.
    time_filter(DateTime, str)
        A Jinja template filter for formatting DateTime objects.
    text_preview(str)
        A Jinja template filter for previewing long text.
    tests(str, str)
        Run unit tests.
"""

import os
import sys
import click
from app import create_app, db
from app.models import *
from flask_migrate import Migrate

# Start coverage when testing if necessary
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# Shell context processor
@app.shell_context_processor
def make_shell_context():
    """
    Application shell context processor to make database model classes accessible.

    Creating the shell context allows for model classes to be accessed from the shell
    without being imported.

    :return dict: A dictionary containing all classes from app.models.
    """
    return dict(db=db, User=User, Role=Role, Post=Post, Tag=Tag)


# Register a time formatting filter with Jinja so it can be called from a pages HTML template
@app.template_filter('time')
def time_filter(time, format="%B %-d, %Y at %-I:%M %p"):
    """
    Format a DateTime object to display a post's time of creation in nicer format.

    :param DateTime time: A DataTime object from a post's time attribute.
    :param str format: A formatting string for a date and time.
    :return str: The post's date and time of creation, formatted.
    """

    return time.strftime(format)


app.jinja_env.filters['time'] = time_filter


# Register a post preview filter with Jinja so it can be called from a pages HTML template
@app.template_filter('preview')
def text_preview(text):
    """
    Create a preview of a post's body.

    Outside of the post's permalink page, only the first 2000 characters should be
    displayed. If a post is shorter than 2000 characters, then the entire post can be returned.
    :param str text: The entire body of a post.
    :return str: The first 2000 characters of a post, plus an ellipses to indicate continuation
    """

    if len(text) < 2000:
        return text
    else:
        return text[0:2000] + '...'


app.jinja_env.filters['time'] = time_filter

# Register command line commands for testing
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
@click.option('--selenium', is_flag=True, default=False, help='Run Selenium tests.')
def test(coverage, selenium):
    """
    Run unit tests.

    By default, unit tests from test directory will be run. If the --selenium argument
    is used, tests from test/selenium will be run. Tests are separated due to threading
    issues in the Selenium script.

    If the --coverage argument is used, tests will be run wuth coverage.

    :arg selenium: Flag indicating that Selenium test scripts should be run.
    :arg coverage: Flag indicating that tests should be run with coverage.
    """
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'  # Set coverage env variable
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    if selenium:    # Run Selenium tests
        tests = unittest.TestLoader().discover('tests/selenium')
    else:   # Run standard unit tests
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV: # Run with coverage
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
