"""Parsers and serializers for /auth API endpoints."""
from flask_restplus import fields, reqparse
from flask_restplus.reqparse import Argument
from flask_restplus.inputs import email

from app.api.auth import auth_ns
from app.util.regex import DB_NAME_REGEX


email_arg = Argument(
    name='email',
    dest='email',
    type=email(),
    location='form',
    required=True,
    nullable=False,
    help='User email address.'
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

user_reqparser = reqparse.RequestParser(bundle_errors=True)
user_reqparser.add_argument(email_arg)
user_reqparser.add_argument(password_arg)

user_model = auth_ns.model(
    'User', {
        'email': fields.String,
        'public_id': fields.String,
        'admin': fields.Boolean,
        'registered_on': fields.String(attribute='registered_on_str')})