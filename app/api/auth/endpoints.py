"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus

from flask import request
from flask_restplus import Resource

from app.api.auth import auth_ns
from app.api.auth.dto import login_reqparser, user_reqparser
from app.api.auth.business import (
    register_new_user, process_login, process_logout, get_logged_in_user
)


@auth_ns.route('/register')
@auth_ns.doc(responses={
    HTTPStatus.BAD_REQUEST: 'Validation error.',
    HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.',
    HTTPStatus.CREATED: 'New user was successfully created.',
    HTTPStatus.CONFLICT: 'Email address is already registered.'})
class RegisterUser(Resource):
    """Register a new user."""

    @auth_ns.doc('register a new user')
    @auth_ns.expect(user_reqparser, validate=True)
    def post(self):
        """Register a new user."""
        args = user_reqparser.parse_args()
        return register_new_user(data=args)


@auth_ns.route('/login')
@auth_ns.doc(responses={
    HTTPStatus.BAD_REQUEST: 'Validation error.',
    HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.',
    HTTPStatus.OK: 'Login succeeded.',
    HTTPStatus.UNAUTHORIZED: 'Email or password does not match.'})
class LoginUser(Resource):
    """User Login Resource."""

    @auth_ns.doc('user login')
    @auth_ns.expect(login_reqparser, validate=True)
    def post(self):
        """Authenticate user and return a session token."""
        args = login_reqparser.parse_args()
        return process_login(data=args)


@auth_ns.route('/logout')
@auth_ns.doc(
    responses={
    HTTPStatus.BAD_REQUEST: 'Validation error.',
    HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.',
    HTTPStatus.OK: 'Log out succeeded, token is no longer valid.',
    HTTPStatus.UNAUTHORIZED: 'Token is invalid or expired.'})
class LogoutUser(Resource):
    """Logout Resource."""

    @auth_ns.doc('user logout', security="Bearer")
    def post(self):
        """Add token to blacklist, deauthenticating the current user."""
        return process_logout()


@auth_ns.route('/status')
@auth_ns.doc(
    responses={
    HTTPStatus.BAD_REQUEST: 'Validation error.',
    HTTPStatus.OK: 'Token is currently valid.',
    HTTPStatus.UNAUTHORIZED: 'Token is invalid or expired.'})
class AuthStatus(Resource):
    """Check user's authorization status."""

    @auth_ns.doc('check user authentication status', security="Bearer")
    def get(self):
        """Validate a session token."""
        return get_logged_in_user()
