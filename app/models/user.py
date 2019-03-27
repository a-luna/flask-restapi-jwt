"""User model for storing logon credentials and other details."""
import jwt
import uuid
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import current_app
from flask_restplus import abort
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, bcrypt
from app.config import key
from app.models.blacklist_token import BlacklistToken
from app.util.dt_format_strings import DT_STR_FORMAT_NAIVE
from app.util.jwt_functions import get_auth_token
from app.util.result import Result


class User(db.Model):
    """User model for storing logon credentials and other details."""
    __tablename__ = "site_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    public_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))

    @hybrid_property
    def registered_on_str(self):
        return self.registered_on.strftime(DT_STR_FORMAT_NAIVE) \
            if self.registered_on else None

    def __init__(self, email, username, password, admin=False):
        self.email = email
        self.username = username
        self.public_id = str(uuid.uuid4())
        self.password = password
        self.registered_on = datetime.utcnow()
        self.admin = admin

    def __repr__(self):
        return (
            '<User('
                f'public_id={self.public_id}, '
                f'username={self.username}, '
                f'email={self.email}'
            ')>')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password,
            current_app.config.get('BCRYPT_LOG_ROUNDS')).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        """Generate auth token."""
        try:
            now = datetime.utcnow()
            expire_time = now + timedelta(
                    hours=current_app.config.get('AUTH_TOKEN_AGE_HOURS'),
                    minutes=current_app.config.get('AUTH_TOKEN_AGE_MINUTES'),
                    seconds=5)
            payload = dict(
                exp=expire_time,
                iat=now,
                sub=self.public_id)
            return jwt.encode(
                payload,
                key,
                algorithm='HS256')
        except Exception as e:
            error = f'Error: {repr(e)}'
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')

    @classmethod
    def decode_auth_token(cls, auth_token):
        """Decode the auth token."""
        if auth_token.startswith('Bearer '):
            split = auth_token.split('Bearer')
            auth_token = split[1].strip()
        if BlacklistToken.check_blacklist(auth_token):
            error = 'Token blacklisted. Please log in again.'
            return Result.Fail(error)
        try:
            payload = jwt.decode(auth_token, key)
            return Result.Ok(payload['sub'])
        except jwt.ExpiredSignatureError:
            error =  'Authorization token expired. Please log in again.'
            return Result.Fail(error)
        except jwt.InvalidTokenError:
            error =  'Invalid token. Please log in again.'
            return Result.Fail(error)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_public_id(cls, public_id):
        return cls.query.filter_by(public_id=public_id).first()