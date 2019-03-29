"""Entry point for the flask application."""
import coverage
import os
import unittest

import click

COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/test/*'
    ]
)
COV.start()

from app import create_app, db
from app.config import APP_FOLDER, APP_ROOT

TEST_FOLDER = APP_FOLDER / 'test'
app = create_app(os.getenv('ENV') or 'dev')

from app.models.blacklist_token import BlacklistToken
from app.models.product import Product
from app.models.user import User


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
        covdir = APP_ROOT / 'tmp' / 'coverage'
        COV.html_report(directory=str(covdir))
        print('\nHTML version: file://%s/index.html' % covdir)
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