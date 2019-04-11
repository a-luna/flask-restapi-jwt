"""Entry point for the flask application."""
import os
import unittest
from coverage import coverage
from pathlib import Path

import click
from Cryptodome.PublicKey import RSA

cov = coverage(branch=True, include="app/*")
cov.start()

from app import create_app, db

app = create_app(os.getenv("ENV") or "dev")

from app.models.blacklist_token import BlacklistToken
from app.models.product import Product
from app.models.user import User
from create_pem import create_public_key_file

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
def test_cov():
    """Run unit tests and calculate code coverage."""
    tests = unittest.TestLoader().discover(TEST_FOLDER)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        cov.stop()
        cov.save()
        print("Coverage Summary:")
        cov.report()
        cov.html_report(directory=str(COV_FOLDER))
        print(f"\nHTML version: file://{COV_FOLDER}/index.html")
        cov.erase()
        return 0
    return 1


@app.cli.command()
@click.option(
    "--key-size",
    type=click.Choice(["2048", "4096"]),
    prompt="Choose the length of the key to generate",
)
def key_gen(key_size):
    """Generate a new RSA key for encoding auth tokens.

    This function generates a new RSA key and outputs the RSA parameters of the key
    to the terminal. The output can be directly copied and pasted into the .env file
    in the project root, making the values available as environment variables. If
    the .env file does not contain any RSA parameters, JWT auth tokens will be encoded
    using the SECRET_KEY environment variable/flask app config value.

    For reference, the meaning of the RSA parameters is given below:
        key.n = modulus
        key.e = public_exponent
        key.d = private_exponent
        key.p = first_prime_number
        key.q = second_prime_number
        key.u = q_inv_crt
    """
    key = RSA.generate(int(key_size))
    print("Add the entries below to your .env file:\n")
    print(f'JWT_KEY_N="{key.n}"')
    print(f'JWT_KEY_E="{key.e}"')
    print(f'JWT_KEY_D="{key.d}"')
    print(f'JWT_KEY_P="{key.p}"')
    print(f'JWT_KEY_Q="{key.q}"')
    print(f'JWT_KEY_U="{key.u}"')
    print(
        '\nPLEASE NOTE: After updating the .env file, you must create a new public.pem file by running "flask create-pem"'
    )
    return key


@app.cli.command()
def create_pem():
    """Create public.pem file in static folder.

    You should create a new public.pem file whenever you change the RSA key values stored
    in the .env file. The public.pem file is used by external services to verify the
    integrity of auth tokens issued by this service. If the public.pem file is not updated
    when RSA key values change, external services will consider auth tokens to be invalid since
    decoding will produce an InvalidTokenError.
    """
    result = create_public_key_file()
    if not result["success"]:
        print(result["error"])
        return 1
    return 0


@app.shell_context_processor
def make_shell_context():
    return {
        "app": app,
        "db": db,
        "BlacklistToken": BlacklistToken,
        "Product": Product,
        "User": User,
    }
