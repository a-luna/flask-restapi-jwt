import time
import json
import unittest
from http import HTTPStatus

from app import db
from app.models.blacklist_token import BlacklistToken
from app.models.user import User
from app.test.base import BaseTestCase


def register_user_happy_path(self):
    register_response = register_user(
        self,
        'new_user@email.com',
        'new_user',
        'test1234')
    register_data = register_response.get_json()
    self.assertEqual(register_data['status'], 'success')
    self.assertEqual(register_data['message'], 'Successfully registered.')
    self.assertIsNotNone(register_data['Authorization'])
    self.assertEqual(register_response.content_type, 'application/json')
    self.assertEqual(register_response.status_code, HTTPStatus.CREATED)
    return register_data['Authorization']

def login_user_heppy_path(self):
    login_response = login_user(self, 'new_user@email.com', 'test1234')
    login_data = login_response.get_json()
    self.assertEqual(login_data['status'], 'success')
    self.assertEqual(login_data['message'], 'Successfully logged in.')
    self.assertIsNotNone(login_data['Authorization'])
    self.assertEqual(login_response.content_type,'application/json')
    self.assertEqual(login_response.status_code, HTTPStatus.OK)
    return login_data['Authorization']

def register_user(self, email, username, password):
    form_data = f'email={email}&username={username}&password={password}'
    return self.client.post(
        'api/v1/auth/register',
        data=form_data,
        content_type='application/x-www-form-urlencoded')

def login_user(self, email, password):
    form_data = f'email={email}&password={password}'
    return self.client.post(
        'api/v1/auth/login',
        data=form_data,
        content_type='application/x-www-form-urlencoded')


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        with self.client:
            register_user_happy_path(self)

    def test_registration_with_already_registered_user(self):
        user = User(
            email='new_user@email.com',
            username='new_user',
            password='test1234')
        db.session.add(user)
        db.session.commit()
        with self.client:
            register_response = register_user(
                self,
                'new_user@email.com',
                'new_user',
                'test1234')
            register_data = register_response.get_json()
            self.assertEqual(register_data['status'], 'fail')
            self.assertEqual(
                register_data['message'],
                '"new_user@email.com" is already registered. Please Log in.')
            self.assertEqual(register_response.content_type, 'application/json')
            self.assertEqual(register_response.status_code, HTTPStatus.CONFLICT)

    def test_registered_user_login(self):
        with self.client:
            register_user_happy_path(self)
            login_user_heppy_path(self)

    def test_non_registered_user_login(self):
        with self.client:
            login_response = login_user(
                self,
                'new_user@email.com',
                'test1234')
            login_data = login_response.get_json()
            self.assertEqual(login_data['status'], 'fail')
            self.assertEqual(login_data['message'], 'email or password does not match.')
            self.assertEqual(login_response.content_type, 'application/json')
            self.assertEqual(login_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status(self):
        with self.client:
            jwt_auth = register_user_happy_path(self)
            auth_status_response = self.client.get(
                'api/v1/auth/status',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data['status'], 'success')
            self.assertIsNotNone(auth_status_data['data'])
            self.assertEqual(
                auth_status_data['data']['email'],
                'new_user@email.com')
            self.assertFalse(auth_status_data['data']['admin'])
            self.assertEqual(auth_status_response.status_code, HTTPStatus.OK)

    def test_auth_status_malformed_bearer_token_1(self):
        with self.client:
            auth_status_response = self.client.get(
                'api/v1/auth/status',
                headers=dict(Authorization='Bearer ad2321dkfad..dgredf324df'))
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data['status'], 'fail')
            self.assertEqual(auth_status_data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_auth_status_malformed_bearer_token_2(self):
        with self.client:
            bad_token = (
                'Bearer eyJ0eXAiOiJKV1QiLCJqbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTMw'
                'MTk0MzIsImlhdCI6MTU1MzAxODUyNywic3ViIjoiNTcwZWI3M2ItYqRiNC00'
                'Yzg2LWIzNWQtMzkwYjQ3ZDk5YmY2In0.mbRr2TJQjUJUGHqswG64DojYh_tk'
                'H7-auTJppuzN82g')
            auth_status_response = self.client.get(
                'api/v1/auth/status',
                headers=dict(Authorization=bad_token))
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data['status'], 'fail')
            self.assertEqual(auth_status_data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_logout(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            logout_response = self.client.post(
                'api/v1/auth/logout',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            logout_data = json.loads(logout_response.data.decode())
            self.assertEqual(logout_data['status'], 'success')
            self.assertEqual(logout_data['message'], 'Successfully logged out.')
            self.assertEqual(logout_response.status_code, HTTPStatus.OK)

    def test_invalid_logout(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            time.sleep(6)
            logout_response = self.client.post(
                'api/v1/auth/logout',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data['status'], 'fail')
            self.assertEqual(
                logout_data['message'],
                'Authorization token expired. Please log in again.')
            self.assertEqual(logout_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_blacklisted_token_logout(self):
        with self.client:
            register_user_happy_path(self)
            jwt_auth = login_user_heppy_path(self)
            blacklist_token = BlacklistToken(token=jwt_auth)
            db.session.add(blacklist_token)
            db.session.commit()
            logout_response = self.client.post(
                'api/v1/auth/logout',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            logout_data = logout_response.get_json()
            self.assertEqual(logout_data['status'], 'fail')
            self.assertEqual(logout_data['message'],'Token blacklisted. Please log in again.')
            self.assertEqual(logout_response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_valid_blacklisted_token_user(self):
        with self.client:
            jwt_auth = register_user_happy_path(self)
            blacklist_token = BlacklistToken(token=jwt_auth)
            db.session.add(blacklist_token)
            db.session.commit()
            auth_status_response = self.client.get(
                'api/v1/auth/status',
                headers=dict(Authorization=f'Bearer {jwt_auth}'))
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data['status'], 'fail')
            self.assertEqual(auth_status_data['message'], 'Token blacklisted. Please log in again.')
            self.assertEqual(auth_status_response.status_code, HTTPStatus.UNAUTHORIZED)


if __name__ == '__main__':
    unittest.main()