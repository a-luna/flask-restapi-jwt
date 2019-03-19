"""Parsers and serializers for /auth API endpoints."""
from flask_restplus import fields, reqparse
from flask_restplus.inputs import email

from app.api.auth import auth_ns
from app.util.datetime_functions import convert_dt_for_display
from app.util.string_functions import parse_auth_token
from app.util.regex import DB_OBJECT_NAME_PATTERN, DB_OBJECT_NAME_REGEX, JWT_REGEX


def json_web_token(token):
    """Return token if valid, raise an excaption if validation fails."""
    result = parse_auth_token(token)
    if result.failure:
        return ValueError(
            f'"{token}"" is not the correct format for a JWT (must be '
            'xxxxx.yyyyy.zzzzz).')
    token = result.value

    if JWT_REGEX.match(token):
        return token
    else:
        return ValueError(
            f'"{token}"" is not the correct format for a JWT (must be '
            'xxxxx.yyyyy.zzzzz).')

    # Swagger documentation
    json_web_token.__schema__ = {'type': 'string', 'format': 'json_web_token'}

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
    type=json_web_token,
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
