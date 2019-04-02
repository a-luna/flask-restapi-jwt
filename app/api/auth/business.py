from datetime import datetime
from http import HTTPStatus

from flask import request
from flask_restplus import abort

from app import db
from app.models.blacklist_token import BlacklistToken
from app.models.user import User


def register_new_user(data):
    if User.find_by_email(data['email']):
        error = f'"{data["email"]}" is already registered. Please Log in.'
        abort(HTTPStatus.CONFLICT, error, status='fail')
    try:
        new_user = User(
            email=data['email'],
            username=data['username'],
            password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return generate_token(new_user)
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')

def generate_token(user):
    try:
        auth_token = user.encode_auth_token()
        response_data = dict(
            status='success',
            message='Successfully registered.',
            email=user.email,
            public_id=user.public_id,
            Authorization=auth_token.decode())
        return response_data, HTTPStatus.CREATED
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')

def process_login(data):
    user = User.find_by_email(data['email'])
    if user and user.check_password(data['password']):
        auth_token = user.encode_auth_token()
        response_data = dict(
            status='success',
            message='Successfully logged in.',
            user=user.public_id,
            Authorization=auth_token.decode())
        return response_data, HTTPStatus.OK
    else:
        error = 'email or password does not match.'
        abort(HTTPStatus.UNAUTHORIZED, error, status='fail')

def process_logout():
    auth_token = get_auth_token()
    check_auth_token(auth_token)
    blacklist_token = BlacklistToken(auth_token)
    try:
        db.session.add(blacklist_token)
        db.session.commit()
        response_dict = dict(
            status='success',
            message='Successfully logged out.')
        return response_dict, HTTPStatus.OK
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')

def get_logged_in_user():
    auth_token = get_auth_token()
    (public_id, _) = check_auth_token(auth_token)
    user = User.find_by_public_id(public_id)
    return user, HTTPStatus.OK

def get_auth_token():
    auth_token = request.headers.get('Authorization')
    if not auth_token:
        error = 'Invalid token. Please log in again.'
        abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
    return auth_token

def check_auth_token(auth_token):
    result = User.decode_auth_token(auth_token)
    if result.failure:
        abort(HTTPStatus.UNAUTHORIZED, result.error, status='fail')
    return result.value

def check_admin_role():
    auth_token = get_auth_token()
    (_, auth) = check_auth_token(auth_token)
    return True if auth else False