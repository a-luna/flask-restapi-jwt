"""Parsers and serializers for /auth API endpoints."""
from flask_restplus import reqparse
from flask_restplus.reqparse import Argument
from flask_restplus.inputs import email

from app.util.regex import DB_NAME_REGEX


def username(name):
    """Return username if valid, raise an excaption if validation fails."""
    if DB_NAME_REGEX.match(name):
        return name
    else:
        raise ValueError(
            f'"{name}" contains one or more invalid characters. Username '
            'must contain only letters (a-z), numbers (0-9), "-" (hyphen '
            'character) and/or "_" (underscore character).')

    # Swagger documentation
    username.__schema__ = {'type': 'string', 'format': 'username'}

email_arg = Argument(
    name='email',
    dest='email',
    type=email(),
    location='form',
    required=True,
    nullable=False,
    help='User email address.'
)

username_arg = Argument(
    name='username',
    dest='username',
    type=username,
    location='form',
    required=True,
    nullable=False
)

password_arg = Argument(
    name='password',
    dest='password',
    type=str,
    location='form',
    required=True,
    nullable=False,
    help='User password.'
)

auth_token_arg = Argument(
    name='Authorization',
    dest='Authorization',
    location='headers',
    required=True,
    nullable=False
)

login_reqparser = reqparse.RequestParser(bundle_errors=True)
login_reqparser.add_argument(email_arg)
login_reqparser.add_argument(password_arg)

token_reqparser = reqparse.RequestParser()
token_reqparser.add_argument(auth_token_arg)

user_reqparser = reqparse.RequestParser(bundle_errors=True)
user_reqparser.add_argument(email_arg)
user_reqparser.add_argument(username_arg)
user_reqparser.add_argument(password_arg)
