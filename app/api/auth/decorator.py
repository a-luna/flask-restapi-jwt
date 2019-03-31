from functools import wraps
from http import HTTPStatus

from flask_restplus import abort

from app.api.auth.business import get_logged_in_user


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, _ = get_logged_in_user()
        if not user.admin:
            error = 'You are not authorized to perform the requested action.'
            abort(HTTPStatus.UNAUTHORIZED, error, status='fail')
        return f(*args, **kwargs)
    return decorated

