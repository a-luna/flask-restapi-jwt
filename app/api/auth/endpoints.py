"""API endpoint definitions for /auth namespace."""
from flask import request
from flask_restplus import Resource

from app.api.auth import auth_ns
from app.api.auth.dto import login_reqparser, token_reqparser, user_reqparser
from app.api.auth.business import (
    register_new_user, process_login, process_logout, get_logged_in_user
)


@auth_ns.route('/register')
@auth_ns.doc(responses={
    400: 'Validation error.',
    500: 'Internal server error.',
    201: 'New user was successfully created.',
    409: 'Email address is already registered.'})
class RegisterUser(Resource):
    """Register a new user."""

    @auth_ns.doc(
        'register a new user',
        parser=user_reqparser,
        validate=True)
    def post(self):
        """Register a new user."""
        args = user_reqparser.parse_args()
        return register_new_user(data=args)


@auth_ns.route('/login')
@auth_ns.doc(responses={
    400: 'Validation error.',
    500: 'Internal server error.',
    200: 'Login succeeded.',
    401: 'Email or password does not match.'})
class LoginUser(Resource):
    """User Login Resource."""

    @auth_ns.doc(
        'user login',
        parser=login_reqparser,
        validate=True)
    def post(self):
        """Authenticate user and return a session token."""
        args = login_reqparser.parse_args()
        return process_login(data=args)


@auth_ns.route('/logout')
@auth_ns.doc(responses={
    400: 'Validation error.',
    500: 'Internal server error.',
    200: 'Log out succeeded, token is no longer valid.',
    401: 'Token is invalid or expired.'})
class LogoutUser(Resource):
    """Logout Resource."""

    @auth_ns.doc(
        'user logout',
        security='Bearer',
        parser=token_reqparser,
        validate=True)
    def post(self):
        """Add token to blacklist, deauthenticating the current user."""
        args = token_reqparser.parse_args()
        return process_logout(args['Authorization'])


@auth_ns.route('/status')
@auth_ns.doc(responses={
    400: 'Validation error.',
    200: 'Token is currently valid.',
    401: 'Token is invalid or expired.'})
class AuthStatus(Resource):
    """Check user's authorization status."""

    @auth_ns.doc(
        'check user authentication statis',
        security='Bearer',
        parser=token_reqparser,
        validate=True)
    def get(self):
        """Validate a session token."""
        args = token_reqparser.parse_args()
        return get_logged_in_user(args['Authorization'])
