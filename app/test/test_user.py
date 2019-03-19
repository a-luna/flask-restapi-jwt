"""Unit tests for User class methods and property behavior."""
import unittest

from app import db
from app.models.user import User
from app.test.base import BaseTestCase


class TestUserModel(BaseTestCase):
    """Unit tests for User class methods and property behavior."""

    def test_user_encode_auth_token(self):
        user = User(
            email='new_user@email.com',
            username='new_user',
            password='test1234'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = User(
            email='newer_user@email.com',
            username='newer_user',
            password='test5678'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))

        result = User.decode_auth_token(auth_token.decode("utf-8"))
        self.assertTrue(result.success)
        self.assertEqual(result.value, user.public_id)


if __name__ == '__main__':
    unittest.main()