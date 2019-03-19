from app import db
from app.models.blacklist_token import BlacklistToken
from app.models.user import User
from app.util.datetime_functions import convert_dt_for_display
from app.util.string_functions import parse_auth_token
from app.util.result import Result

import uuid
from datetime import datetime, timezone

from app import db
from app.models.user import User


def register_new_user(data):
    if User.find_by_email(data['email']):
        error = f'"{data["email"]}" is already registered. Please Log in.'
        response_object = {
            'status': 'fail',
            'message': error}
        return response_object, 409

    new_user = User(
        email=data['email'],
        username=data['username'],
        password=data['password']
    )
    db.session.add(new_user)
    db.session.commit()
    return generate_token(new_user)


def generate_token(user):
    try:
        # generate the auth token
        auth_token = user.encode_auth_token()
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.',
            'Authorization': auth_token.decode()
        }
        return response_object, 201
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': f'Error: {repr(e)}'}
        return response_object, 500


def process_login(data):
    try:
        # fetch the user data
        user = User.find_by_email(data['email'])
        if user and user.check_password(data['password']):
            auth_token = user.encode_auth_token()
            response_object = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'user': user.public_id,
                'Authorization': auth_token.decode()}
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'email or password does not match.'}
            return response_object, 401
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': f'Error: {repr(e)}'}
        return response_object, 500


def process_logout(auth_token):
    result = User.decode_auth_token(auth_token)
    if result.failure:
        response_object = {
            'status': 'fail',
            'message': result.error}
        return response_object, 401

    blacklist_token = BlacklistToken(auth_token)
    try:
        db.session.add(blacklist_token)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Successfully logged out.'}
        return response_object, 200
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': f'Error: {repr(e)}'}
        return response_object, 500


def get_logged_in_user(auth_token):
        result = User.decode_auth_token(auth_token)
        if result.failure:
            response_object = {
            'status': 'fail',
            'message': result.error}
            return response_object, 401

        user_public_id = result.value
        user = User.find_by_public_id(user_public_id)
        response_object = {
            'status': 'success',
            'data': {
                'user_id': user.id,
                'email': user.email,
                'admin': user.admin,
                'registered_on':
                    convert_dt_for_display(user, 'registered_on')}}
        return response_object, 200

