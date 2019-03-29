from functools import wraps
from http import HTTPStatus

from flask import request
from flask_restplus import abort

from app.api.auth.business import get_logged_in_user


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            error = 'Please provide a valid auth token.'
            abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
        data, _ = get_logged_in_user(auth_token)
        user_data = data.get('data')
        admin = user_data.get('admin')
        if not admin:
            error = 'You are not authorized to perform the requested action.'
            abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
        return f(*args, **kwargs)
    return decorated

