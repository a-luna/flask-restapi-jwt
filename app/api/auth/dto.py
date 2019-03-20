"""Parsers and serializers for /auth API endpoints."""
from flask_restplus import reqparse
from flask_restplus.inputs import email

from app.util.regex import DB_OBJECT_NAME_REGEX


def username(name):
    """Return username if valid, raise an excaption if validation fails."""
    if DB_OBJECT_NAME_REGEX.match(name):
        return name
    else:
        raise ValueError(
            f'"{name}" contains one or more invalid characters. Username '
            'must contain only letters (a-z), numbers (0-9), "-" (hyphen '
            'character) and/or "_" (underscore character).')

    # Swagger documentation
    username.__schema__ = {'type': 'string', 'format': 'username'}


login_reqparser = reqparse.RequestParser(bundle_errors=True)
login_reqparser.add_argument(
    name='email',
    dest='email',
    type=email(),
    location='form',
    required=True,
    nullable=False,
    help='User email address.'
)
login_reqparser.add_argument(
    name='password',
    dest='password',
    type=str,
    location='form',
    required=True,
    nullable=False,
    help='User password.'
)

token_reqparser = reqparse.RequestParser()
token_reqparser.add_argument(
    name='Authorization',
    dest='Authorization',
    location='headers',
    required=True,
    nullable=False
)

user_reqparser = reqparse.RequestParser(bundle_errors=True)
user_reqparser.add_argument(
    name='email',
    dest='email',
    type=email(),
    location='form',
    required=True,
    nullable=False
)
user_reqparser.add_argument(
    name='username',
    dest='username',
    type=username,
    location='form',
    required=True,
    nullable=False
)
user_reqparser.add_argument(
    name='password',
    dest='password',
    type=str,
    location='form',
    required=True,
    nullable=False
)
