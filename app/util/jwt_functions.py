from app.util.regex import JWT_REGEX
from app.util.result import Result

def get_auth_token(request):
    """Parse auth token from string."""
    data = request.headers.get('Authorization')
    return Result.Ok(data) if data \
        else Result.Fail('Please provide a valid auth token.')
