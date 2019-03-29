"""Compiled regular expressions and patterns."""
import re

DB_NAME_PATTERN = r'^[a-z0-9_-]+$'
DB_NAME_REGEX = re.compile(DB_NAME_PATTERN)
