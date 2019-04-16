"""Decorator that checks authorization token for administrator privileges."""
from functools import wraps
from http import HTTPStatus

from flask_restplus import abort

from app.api.auth.business import check_auth_token


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_dict = check_auth_token()
        if not user_dict["admin"]:
            error = "You are not authorized to perform the requested action."
            abort(HTTPStatus.FORBIDDEN, error, status="fail")
        return f(*args, **kwargs)

    return decorated
