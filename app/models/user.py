"""User model for storing logon credentials and other details."""
import jwt
import uuid
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, bcrypt
from app.models.blacklist_token import BlacklistToken
from app.util.constants import DT_STR_FORMAT_NAIVE
from app.util.crypto import get_private_key, get_public_key
from app.util.result import Result


class User(db.Model):
    """User model for storing logon credentials and other details."""

    __tablename__ = "site_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    public_id = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))

    @hybrid_property
    def registered_on_str(self):
        return (
            self.registered_on.strftime(DT_STR_FORMAT_NAIVE)
            if self.registered_on
            else None
        )

    def __init__(self, email, password, admin=False):
        self.email = email
        self.public_id = str(uuid.uuid4())
        self.password = password
        self.registered_on = datetime.utcnow()
        self.admin = admin

    def __repr__(self):
        return (
            "User<("
            f"email={self.email}, "
            f"public_id={self.public_id}, "
            f"admin={self.admin})>"
        )

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        """Generate auth token."""
        now = datetime.utcnow()
        expire_time = now + timedelta(
            hours=current_app.config.get("AUTH_TOKEN_AGE_HOURS"),
            minutes=current_app.config.get("AUTH_TOKEN_AGE_MINUTES"),
            seconds=5,
        )

        result = get_private_key()
        if result.success:
            key = result.value
            algorithm = "RS256"
        else:
            key = current_app.config.get("SECRET_KEY")
            algorithm = "HS256"

        payload = dict(exp=expire_time, iat=now, sub=self.public_id, admin=self.admin)
        return jwt.encode(payload, key, algorithm=algorithm)

    @staticmethod
    def decode_auth_token(auth_token):
        """Decode the auth token."""
        if auth_token.startswith("Bearer "):
            split = auth_token.split("Bearer")
            auth_token = split[1].strip()
        if BlacklistToken.check_blacklist(auth_token):
            error = "Token blacklisted. Please log in again."
            return Result.Fail(error)

        result = get_public_key()
        if result.success:
            key = result.value
            algorithm = "RS256"
        else:
            key = current_app.config.get("SECRET_KEY")
            algorithm = "HS256"

        try:
            payload = jwt.decode(auth_token, key, algorithms=[algorithm])
            return Result.Ok(dict(public_id=payload["sub"], admin=payload["admin"]))
        except jwt.ExpiredSignatureError:
            error = "Authorization token expired. Please log in again."
            return Result.Fail(error)
        except jwt.InvalidTokenError:
            error = "Invalid token. Please log in again."
            return Result.Fail(error)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_public_id(cls, public_id):
        return cls.query.filter_by(public_id=public_id).first()
