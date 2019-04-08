"""Entry point for the flask application."""
import os
import unittest
from coverage import coverage
from pathlib import Path

COV = coverage(branch=True, include="app/*")
COV.start()

from app import create_app, db

app = create_app(os.getenv("ENV") or "dev")

from app.models.blacklist_token import BlacklistToken
from app.models.product import Product
from app.models.user import User

APP_ROOT = Path(__file__).resolve().parent
TEST_FOLDER = APP_ROOT / "test"
COV_FOLDER = APP_ROOT / "tmp" / "coverage"


@app.cli.command()
def run():
    app.run()


@app.cli.command()
def test():
    """Run unit tests without test coverage."""
    tests = unittest.TestLoader().discover(TEST_FOLDER, pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@app.cli.command()
def cov():
    """Run unit tests and calculate code coverage."""
    tests = unittest.TestLoader().discover(TEST_FOLDER)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        COV.html_report(directory=str(COV_FOLDER))
        print(f"\nHTML version: file://{COV_FOLDER}/index.html")
        COV.erase()
        return 0
    return 1


@app.shell_context_processor
def make_shell_context():
    return {
        "app": app,
        "db": db,
        "BlacklistToken": BlacklistToken,
        "Product": Product,
        "User": User,
    }
