"""Business logic for /auth API endpoints."""
from http import HTTPStatus

from flask import request
from flask_restplus import abort

from app import db
from app.models.blacklist_token import BlacklistToken
from app.models.user import User
from app.util.crypto import decrypt_user_credentials
from app.util.result import Result


def register_new_user(data):
    result = decrypt_user_credentials(data["key"], data["iv"], data["ct"])
    if result.failure:
        abort(HTTPStatus.UNAUTHORIZED, result.error, status="fail")
    user_credentials = result.value
    if User.find_by_email(user_credentials["email"]):
        error = f"{user_credentials['email']} is already registered. Please Log in."
        abort(HTTPStatus.CONFLICT, error, status="fail")
    try:
        new_user = User(
            email=user_credentials["email"], password=user_credentials["password"]
        )
        db.session.add(new_user)
        db.session.commit()
        return generate_token(new_user)
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")


def generate_token(user):
    try:
        auth_token = user.encode_auth_token()
        response_data = dict(
            status="success",
            message="Successfully registered",
            email=user.email,
            public_id=user.public_id,
            Authorization=auth_token.decode(),
        )
        return response_data, HTTPStatus.CREATED
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")


def process_login(data):
    result = decrypt_user_credentials(data["key"], data["iv"], data["ct"])
    if result.failure:
        abort(HTTPStatus.UNAUTHORIZED, result.error, status="fail")
    user_credentials = result.value
    user = User.find_by_email(user_credentials["email"])
    if user and user.check_password(user_credentials["password"]):
        auth_token = user.encode_auth_token()
        response_data = dict(
            status="success",
            message="Successfully logged in",
            user=user.public_id,
            Authorization=auth_token.decode(),
        )
        return response_data, HTTPStatus.OK
    else:
        error = "email or password does not match."
        abort(HTTPStatus.UNAUTHORIZED, error, status="fail")


def process_logout():
    check_auth_token()
    auth_token = request.headers.get("Authorization")
    blacklist_token = BlacklistToken(auth_token)
    try:
        db.session.add(blacklist_token)
        db.session.commit()
        response_dict = dict(status="success", message="Successfully logged out.")
        return response_dict, HTTPStatus.OK
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")


def get_logged_in_user():
    user_dict = check_auth_token()
    user = User.find_by_public_id(user_dict["public_id"])
    return user, HTTPStatus.OK


def check_auth_token():
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        error = "Invalid token. Please log in again."
        abort(HTTPStatus.UNAUTHORIZED, error, status="fail")
    result = User.decode_auth_token(auth_token)
    if result.failure:
        abort(HTTPStatus.UNAUTHORIZED, result.error, status="fail")
    return result.value
