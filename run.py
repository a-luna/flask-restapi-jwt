"""Entry point for the flask application."""
import os
import unittest
from coverage import coverage
from Cryptodome.PublicKey import RSA
from pathlib import Path

COV = coverage(branch=True, include="app/*")
COV.start()

from app import create_app, db

app = create_app(os.getenv("ENV") or "dev")

from app.models.blacklist_token import BlacklistToken
from app.models.product import Product
from app.models.user import User
from app.util.crypto import generate_new_key, create_public_key_file

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


@app.cli.command()
def key_gen(key_size=2048):
    """Generate a new RSA key for encoding auth tokens."""
    result = generate_new_key()
    if result.success:
        print(
            '\nPLEASE NOTE: After updating the .env file, you must create a new public.pem file by running "flask create-pem"'
        )
        return 0
    print(result.error)
    return 1


@app.cli.command()
def create_pem():
    """Create public.pem file in static folder."""
    result = create_public_key_file()
    if result.success:
        print("Successfully created public.pem file in static folder.")
        return 0
    print(result.error)
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
