from functools import wraps
from http import HTTPStatus

from flask import request
from flask_restplus import abort

from app.api.auth.business import check_admin_role


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_admin_role():
            error = 'You are not authorized to perform the requested action.'
            abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
        return f(*args, **kwargs)
    return decorated

