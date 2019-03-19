from datetime import datetime, timezone

from tzlocal import get_localzone

from app.util.dt_format_strings import DT_STR_FORMAT, DT_FORMAT_ISO
from app.util.better_getattr import better_getattr


def get_dt_iso_format_utc(obj, attr_name):
    result = better_getattr(obj, attr_name)
    if not result.failure:
        print(result.error)
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
        print(result['error_message'])
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

def format_timedelta(td):
    td_days = None
    td_str = str(td)
    if 'day' in td_str:
        splat = td_str.split(',')
        td_days = splat[0]
        td_str = splat[1].strip()
    split = td_str.split(':')
    splot = split[2].split('.')
    td_hours = int(split[0])
    td_min = int(split[1])
    td_sec = int(splot[0])

    if td_days:
        return '{d}, {h:02d}:{m:02d}:{s:02d}'.format(
            d=td_days,
            h=td_hours,
            m=td_min,
            s=td_sec
        )
    if td_hours > 0:
        return '{h:02d}:{m:02d}:{s:02d}'.format(
            h=td_hours,
            m=td_min,
            s=td_sec
        )
    return '{m:02d}:{s:02d}'.format(m=td_min, s=td_sec)


def format_timedelta_precise(td):
    td_sec = td.seconds % 60
    td_min = (td.seconds - td_sec) / 60
    td_ms = td.microseconds / 1000
    if td_min > 0:
        return '{:.0f}m {}s'.format(td_min, td_sec)
    elif td_sec > 0:
        return '{}s {:.0f}ms'.format(td.seconds, td_ms)
    return '{:.0f}ms'.format(td_ms)