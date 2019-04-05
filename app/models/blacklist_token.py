"""Token Model for storing JWT tokens."""
from datetime import datetime, timezone

from app import db


class BlacklistToken(db.Model):
    """Token Model for storing JWT tokens."""

    __tablename__ = "blacklist_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.now(timezone.utc)

    def __repr__(self):
        return f"BlacklistToken<(id={self.id}, token={self.token})>"

    @classmethod
    def check_blacklist(cls, auth_token):
        # check whether auth token has been blacklisted
        exists = cls.query.filter_by(token=str(auth_token)).first()
        return True if exists else False
