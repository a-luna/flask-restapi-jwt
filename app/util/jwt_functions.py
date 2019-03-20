from app.util.regex import JWT_REGEX
from app.util.result import Result


def get_auth_token_from_headers(request):
    """Parse auth token from request headers."""
    data = request.headers.get('Authorization')
    if not data:
        error = 'Please provide a valid auth token.'
        return Result.Fail(error)
    return get_auth_token(data)

def get_auth_token(data):
    """Parse auth token from string."""
    match = JWT_REGEX.search(data)
    if not match:
        error = 'Please provide a valid auth token.'
        return Result.Fail(error)
    return Result.Ok(match.group())
