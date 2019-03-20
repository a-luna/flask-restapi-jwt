from functools import wraps
from http import HTTPStatus

from flask import request
from flask_restplus import abort

from app.api.auth.business import get_logged_in_user
from app.util.jwt_functions import get_auth_token_from_headers


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = get_auth_token_from_headers(request)
        if result.failure:
            abort(HTTPStatus.UNAUTHORIZED, result.error, status='fail')
        auth_token = result.value
        data, status = get_logged_in_user(auth_token)
        token = data.get('data')
        if not token:
            return data, status
        admin = token.get('admin')
        if not admin:
            error = 'You do not have administrator access.'
            abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
        return f(*args, **kwargs)
    return decorated

