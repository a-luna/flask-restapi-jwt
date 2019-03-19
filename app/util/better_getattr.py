"""Drop-in replacement for getattr function."""
from app.util.result import Result

def better_getattr(obj, attr_name):
    """Acts exactly as getattr(), but extends to dict objects."""
    if type(obj) is dict and attr_name in obj:
        value = obj[attr_name]
    elif hasattr(obj, attr_name):
        value = getattr(obj, attr_name)
    else:
        error = (
            'Error! Attribute does not exist:\n'
            'Object: {o}, Type: {t}, Attr Name: {a}'
            .format(o=obj, t=type(obj), a=attr_name)
        )
        return Result.Fail(error)
    return Result.Ok(value)
