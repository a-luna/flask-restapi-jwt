from datetime import datetime, timezone

from tzlocal import get_localzone

from app.util.dt_format_strings import DT_STR_FORMAT, DT_FORMAT_ISO
from app.util.better_getattr import better_getattr


def get_dt_iso_format_utc(obj, attr_name):
    result = better_getattr(obj, attr_name)
    if result.failure:
        return ''
    try:
        dt = result.value
        return dt.replace(tzinfo=timezone.utc).strftime(DT_FORMAT_ISO)
    except ValueError:
        return ''
    except OverflowError:
        return ''

def convert_dt_for_display(obj, attr_name, user_tz=None, str_format=DT_STR_FORMAT):
    """Convert a datetime value to formatted string.

    If 'obj' has an attribute 'attr_name' or if 'obj' is a dict and contains
    the key 'attr_name', the datetime value of 'attr_name' will be converted
    to a formatted string using 'str_format'. The default value for
    'str_format' will produce a string like: '01 Jan 2000 00:00 AM PST'.

    If 'attr_name' does not exist or if the value is not a datetime object,
    an empty string is returned.
    """
    result = better_getattr(obj, attr_name)
    if result.failure:
        return ''
    try:
        s = convert_dt_to_user_tz_str(
            result.value,
            user_tz=user_tz,
            str_format=str_format
        )
        return s
    except ValueError:
        return ''
    except OverflowError:
        return ''


def convert_dt_to_user_tz(dt, user_tz=None, str_format=DT_STR_FORMAT):
    if not user_tz:
        user_tz = get_localzone()
    try:
        return dt.replace(tzinfo=timezone.utc).astimezone(user_tz)
    except ValueError:
        return ''
    except OverflowError:
        return ''


def convert_dt_to_user_tz_str(dt, user_tz=None, str_format=DT_STR_FORMAT):
    return convert_dt_to_user_tz(dt, user_tz, str_format).strftime(str_format)
