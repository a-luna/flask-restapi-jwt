from functools import wraps
from flask import request

from app.api.auth.business import get_logged_in_user
from app.util.result import Result
from app.util.string_functions import parse_auth_token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = get_auth_token(request)
        if result.failure:
            return result
        data, status = get_logged_in_user(result.value)
        token = data.get('data')
        if not token:
            return data, status
        return f(*args, **kwargs)
    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = get_auth_token(request)
        if result.failure:
            return result
        data, status = get_logged_in_user(result.value)
        token = data.get('data')
        if not token:
            return data, status
        admin = token.get('admin')
        if not admin:
            response_object = {
                'status': 'fail',
                'message': 'admin token required'
            }
            return response_object, 401
        return f(*args, **kwargs)
    return decorated


def get_auth_token(request):
    data = request.headers.get('Authorization')
    if not data:
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'}
        return Result.Fail((response_object, 403))

    parse_result = parse_auth_token(data)
    if parse_result.failure:
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'}
        return Result.Fail((response_object, 401))
    return Result.Ok(parse_result.value)