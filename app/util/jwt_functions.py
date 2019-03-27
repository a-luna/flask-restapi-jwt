from app.util.regex import JWT_REGEX
from app.util.result import Result

def get_auth_token(request):
    """Parse auth token from string."""
    data = request.headers.get('Authorization')
    if not data:
        error = 'Please provide a valid auth token.'
        return Result.Fail(error)
    return Result.Ok(data)
