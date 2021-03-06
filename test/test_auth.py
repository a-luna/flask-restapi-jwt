"""Unit tests for /auth API endpoints."""
import json
import time
import unittest
from http import HTTPStatus

from app import db
from app.models.blacklist_token import BlacklistToken
from app.models.user import User
from app.util.crypto import encrypt_user_credentials
from test.base import BaseTestCase


def register_user_happy_path(self):
    register_response = register_user(self, "new_user@email.com", "test1234")
    register_data = register_response.get_json()
    self.assertEqual(register_data["status"], "success")
    self.assertEqual(register_data["message"], "Successfully registered")
    self.assertIsNotNone(register_data["Authorization"])
    self.assertEqual(register_response.content_type, "application/json")
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)
    return register_data["Authorization"]


def login_user_heppy_path(self):
    login_response = login_user(self, "new_user@email.com", "test1234")
    login_data = login_response.get_json()
    self.assertEqual(login_data["status"], "success")
    self.assertEqual(login_data["message"], "Successfully logged in")
    self.assertIsNotNone(login_data["Authorization"])
    self.assertEqual(login_response.content_type, "application/json")
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data["Authorization"]


def register_user(self, email, password):
    result = encrypt_user_credentials(email, password)
    if result.failure:
        self.fail(f"Error: {repr(result.error)}")
    enc_user_creds = result.value
    return self.client.post(
        "api/v1/auth/register",
        data=json.dumps(enc_user_creds),
        content_type="application/json",
    )


def login_user(self, email, password):
    result = encrypt_user_credentials(email, password)
    if result.failure:
        self.fail(f"Error: {repr(result.error)}")
    enc_user_creds = result.value
    return self.client.post(
        "api/v1/auth/login",
        data=json.dumps(enc_user_creds),
        content_type="application/json",
    )


class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        with self.client:
            register_user_happy_path(self)
            new_user = User.find_by_email("new_user@email.com")
            self.assertIsNotNone(new_user)
            new_user_repr = (
                f"User<("
                f"email={new_user.email}, "
                f"public_id={new_user.public_id}, "
                f"admin=False)>"
            )
            self.assertEqual(repr(new_user), new_user_repr)
            with self.assertRaises(AttributeError):
                _ = new_user.password

    def test_registration_email_already_registered(self):
        with self.client:
            user = User(email="new_user@email.com", password="test1234")
            db.session.add(user)
            db.session.commit()
            register_response = register_user(self, "new_user@email.com", "test1234")
            register_data = register_response.get_json()
            self.assertEqual(register_data["status"], "fail")
            self.assertEqual(
                register_data["message"],
                "new_user@email.com is already registered. Please Log in.",
            )
            self.assertEqual(register_response.content_type, "application/json")
            self.assertEqual(register_response.status_code, HTTPStatus.CONFLICT)

    def test_login(self):
        with self.client:
            register_user_happy_path(self)
            login_user_heppy_path(self)

    def test_login_email_does_not_exist(self):
        with self.client:
            login_response = login_user(self, "new_user@email.com", "test1234")
            login_data = login_response.get_json()
            self.assertEqual(login_data["status"], "fail")
            self.assertEqual(login_data["message"], "email or password does not match.")
            self.assertEqual(login_response.content_type, "application/json")
            self.assertEqual(login_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status(self):
        with self.client:
            jwt_auth = register_user_happy_path(self)
            auth_status_response = self.client.get(
                "api/v1/auth/status", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["email"], "new_user@email.com")
            self.assertFalse(auth_status_data["admin"])
            self.assertEqual(auth_status_response.status_code, HTTPStatus.OK)

    def test_auth_status_malformed_token_1(self):
        with self.client:
            auth_status_response = self.client.get(
                "api/v1/auth/status",
                headers=dict(Authorization="Bearer ad2321dkfad..dgredf324df"),
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["status"], "fail")
            self.assertEqual(
                auth_status_data["message"], "Invalid token. Please log in again."
            )
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status_malformed_token_2(self):
        with self.client:
            bad_token = (
                "eyJ0eXAiOiJKV1QiLCJqbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTMw"
                "MTk0MzIsImlhdCI6MTU1MzAxODUyNywic3ViIjoiNTcwZWI3M2ItYqRiNC00"
                "Yzg2LWIzNWQtMzkwYjQ3ZDk5YmY2In0.mbRr2TJQjUJUGHqswG64DojYh_tk"
                "H7-auTJppuzN82g"
            )
            auth_status_response = self.client.get(
                "api/v1/auth/status", headers=dict(Authorization=bad_token)
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["status"], "fail")
            self.assertEqual(
                auth_status_data["message"], "Invalid token. Please log in again."
            )
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status_token_blacklisted(self):
        with self.client:
            jwt_auth = register_user_happy_path(self)
            blacklist_token = BlacklistToken(token=jwt_auth)
            db.session.add(blacklist_token)
            db.session.commit()
            auth_status_response = self.client.get(
                "api/v1/auth/status", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["status"], "fail")
            self.assertEqual(
                auth_status_data["message"], "Token blacklisted. Please log in again."
            )
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status_no_token(self):
        with self.client:
            auth_status_response = self.client.get("api/v1/auth/status")
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["status"], "fail")
            self.assertEqual(
                auth_status_data["message"], "Invalid token. Please log in again."
            )
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_algorithm_hs256(self):
        with self.client:
            # verify auth token still created when rsa parameter missing
            self.app.config["JWT_KEY_N"] = None
            jwt_auth = register_user_happy_path(self)
            self.assertIsNotNone(jwt_auth)
            auth_status_response = self.client.get(
                "api/v1/auth/status", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["email"], "new_user@email.com")
            self.assertFalse(auth_status_data["admin"])
            self.assertEqual(auth_status_response.status_code, HTTPStatus.OK)

    def test_logout(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            logout_response = self.client.post(
                "api/v1/auth/logout", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data["status"], "success")
            self.assertEqual(logout_data["message"], "Successfully logged out.")
            self.assertEqual(logout_response.status_code, HTTPStatus.OK)

    def test_logout_auth_token_expired(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            time.sleep(6)
            logout_response = self.client.post(
                "api/v1/auth/logout", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data["status"], "fail")
            self.assertEqual(
                logout_data["message"],
                "Authorization token expired. Please log in again.",
            )
            self.assertEqual(logout_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_logout_token_blacklisted(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            blacklist_token = BlacklistToken(token=jwt_auth)
            token_repr = (
                f"BlacklistToken<("
                f"id={blacklist_token.id}, "
                f"token={blacklist_token.token})>"
            )
            self.assertEqual(repr(blacklist_token), token_repr)

            db.session.add(blacklist_token)
            db.session.commit()
            logout_response = self.client.post(
                "api/v1/auth/logout", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data["status"], "fail")
            self.assertEqual(
                logout_data["message"], "Token blacklisted. Please log in again."
            )
            self.assertEqual(logout_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_logout_no_token(self):
        with self.client:
            logout_response = self.client.post("api/v1/auth/logout")
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data["status"], "fail")
            self.assertEqual(
                logout_data["message"], "Invalid token. Please log in again."
            )
            self.assertEqual(logout_response.status_code, HTTPStatus.UNAUTHORIZED)


if __name__ == "__main__":
    unittest.main()
