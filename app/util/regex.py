"""Compiled regular expressions and patterns."""
import re

URL_PATTERN = (
    r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?'
    r'[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
)
URL_REGEX = re.compile(URL_PATTERN)
JWT_REGEX = re.compile(
    r'[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
)
VERSION_NUMBER_REGEX = re.compile(r'(?:(\d+\.(?:\d+\.)*\d+[a-zA-Z]{0,1}))')
GUID_REGEX = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
)
DB_OBJECT_NAME_PATTERN = r'^[a-z0-9_-]+$'
DB_OBJECT_NAME_REGEX = re.compile(DB_OBJECT_NAME_PATTERN)


def string_is_null_or_blank(string):
    """Check if a string is null or consists entirely of whitespace."""
    return not string or string.isspace()


def sanitize_url(scraped_url):
    if string_is_null_or_blank(scraped_url):
        return None
    match = URL_REGEX.match(scraped_url)
    return match.group() if match else None


def sanitize_version_number(scraped_ver_num):
    if string_is_null_or_blank(scraped_ver_num):
        return None
    match = VERSION_NUMBER_REGEX.search(scraped_ver_num)
    return match.group() if match else None
