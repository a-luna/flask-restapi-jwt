"""Entry point for the flask application."""
import coverage
import os
import unittest
from pathlib import Path

import click

from app import create_app, db
from app.config import APP_FOLDER

TEST_FOLDER = APP_FOLDER / 'test'
app = create_app(os.getenv('ENV') or 'dev')

from app.models.blacklist_token import BlacklistToken
from app.models.product import Product
from app.models.user import User


COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/test/*',
        'app/config.py',
        'app/*/__init__.py'
    ]
)
COV.start()

@app.cli.command()
def run():
    app.run()

@app.cli.command()
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover(TEST_FOLDER, pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@app.cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover(TEST_FOLDER)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1

@app.shell_context_processor
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'BlacklistToken': BlacklistToken,
        'Product': Product,
        'User': User
    }