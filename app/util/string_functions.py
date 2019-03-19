from app.util.result import Result

def parse_auth_token(data):
    """Parse auth token from header data."""
    if 'Bearer' in data:
        split = data.split(" ")
        if len(split) == 2:
            return Result.Ok(split[1])
        else:
            error = f'Unable to arse auth token from header data: {data}'
            return Result.Fail(error)
    else:
        return Result.Ok(data)

def string_is_null_or_blank(s):
    """Check if a string is null or consists entirely of whitespace."""
    return not s or s.isspace()