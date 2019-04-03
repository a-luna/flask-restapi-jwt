"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus

from flask import request
from flask_restplus import Resource

from app.api.auth import auth_ns
from app.api.auth.dto import user_reqparser, user_model
from app.api.auth.business import (
    register_new_user, process_login, process_logout, get_logged_in_user
)


@auth_ns.route('/register')
class RegisterUser(Resource):
    """Register a new user."""

    @auth_ns.doc(
        'register a new user',
        responses={
            HTTPStatus.CREATED: 'New user was successfully created.',
            HTTPStatus.BAD_REQUEST: 'Validation error.',
            HTTPStatus.CONFLICT: 'Email address is already registered.',
            HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.'})
    @auth_ns.expect(user_reqparser, validate=True,)
    def post(self):
        """Register a new user."""
        args = user_reqparser.parse_args()
        return register_new_user(data=args)


@auth_ns.route('/login')
class LoginUser(Resource):
    """User Login Resource."""

    @auth_ns.doc(
        'user login',
        responses={
            HTTPStatus.OK: 'Login succeeded.',
            HTTPStatus.BAD_REQUEST: 'Validation error.',
            HTTPStatus.UNAUTHORIZED: 'Email or password does not match.',
            HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.'})
    @auth_ns.expect(user_reqparser, validate=True)
    def post(self):
        """Authenticate user and return a session token."""
        args = user_reqparser.parse_args()
        return process_login(data=args)


@auth_ns.route('/logout')
class LogoutUser(Resource):
    """Logout Resource."""

    @auth_ns.doc(
        'user logout',
        security='Bearer',
        responses={
            HTTPStatus.OK: 'Log out succeeded, token is no longer valid.',
            HTTPStatus.BAD_REQUEST: 'Validation error.',
            HTTPStatus.UNAUTHORIZED: 'Token is invalid or expired.',
            HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error.'})
    def post(self):
        """Add token to blacklist, deauthenticating the current user."""
        return process_logout()


@auth_ns.route('/status')
class AuthStatus(Resource):
    """Check user's authorization status."""

    @auth_ns.doc(
        'check user authentication status',
        security='Bearer',
        responses={
            HTTPStatus.BAD_REQUEST: 'Validation error.',
            HTTPStatus.UNAUTHORIZED: 'Token is invalid or expired.'})
    @auth_ns.marshal_with(
        user_model,
        code=HTTPStatus.OK,
        description='Token is currently valid.')
    def get(self):
        """Validate a session token."""
        return get_logged_in_user()
