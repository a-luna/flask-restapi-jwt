"""Parsers and serializers for /product API endpoints."""
from flask_restplus import fields, reqparse
from flask_restplus.reqparse import Argument
from flask_restplus.inputs import URL

from app.api.product import product_ns
from app.util.datetime_functions import get_dt_iso_format_utc
from app.util.regex import DB_OBJECT_NAME_PATTERN, DB_OBJECT_NAME_REGEX


def product_name(name):
    """Return name if valid, raise an excaption if validation fails."""
    if DB_OBJECT_NAME_REGEX.match(name):
        return name
    else:
        raise ValueError(
            f'"{name}" contains one or more invalid characters. Product name '
            'must contain only letters (a-z), numbers (0-9), "-" (hyphen '
            'character) and/or "_" (underscore character).'
        )

    # Swagger documntation
    product_name.__schema__ = {'type': 'string', 'format': 'product_name'}


def xpath_query(xpath):
    """Return xpath if valid, raise an excaption if validation fails."""
    if xpath and not xpath.isspace():
        return xpath
    else:
        raise ValueError('XPath query must not be null or empty string.')

    # Swagger documntation
    xpath_query.__schema__ = {'type': 'string', 'format': 'xpath_query'}

json_web_token_arg = Argument(
    name='Authorization',
    dest='Authorization',
    location='headers',
    required=True,
    nullable=False
)

product_name_arg = Argument(
    name='product_name',
    dest='product_name',
    type=product_name,
    location='form',
    required=True,
    nullable=False,
    case_sensitive=False
)

release_info_url_arg = Argument(
    name='release_info_url',
    dest='release_info_url',
    type=URL(schemes=['http', 'https']),
    location='form',
    required=True,
    nullable=False
)

xpath_version_number_arg = Argument(
    name='xpath_version_number',
    dest='xpath_version_number',
    type=xpath_query,
    location='form',
    required=True,
    nullable=False
)

xpath_download_url_arg = Argument(
    name='xpath_download_url',
    dest='xpath_download_url',
    type=xpath_query,
    location='form',
    required=True,
    nullable=False
)

post_product_parser = reqparse.RequestParser(bundle_errors=True)
post_product_parser.add_argument(json_web_token_arg)
post_product_parser.add_argument(product_name_arg)
post_product_parser.add_argument(release_info_url_arg)
post_product_parser.add_argument(xpath_version_number_arg)
post_product_parser.add_argument(xpath_download_url_arg)

put_product_parser = reqparse.RequestParser(bundle_errors=True)
put_product_parser.add_argument(json_web_token_arg)
put_product_parser.add_argument(release_info_url_arg)
put_product_parser.add_argument(xpath_version_number_arg)
put_product_parser.add_argument(xpath_download_url_arg)

delete_product_parser = reqparse.RequestParser(bundle_errors=True)
delete_product_parser.add_argument(json_web_token_arg)

product_api_model = product_ns.model(
    'get_product',
    {
        'product_name': fields.String(
            required=True,
            min_length=3,
            pattern=DB_OBJECT_NAME_PATTERN
        ),
        'newest_version_number': fields.String(
            readonly=True,
            required=False
        ),
        'download_url': fields.String(
            readonly=True,
            required=False
        ),
        'last_checked': fields.String(
            attribute=lambda x: get_dt_iso_format_utc(x, 'last_checked'),
            default='',
            readonly=True,
            required=False
        ),
        'last_update': fields.String(
            attribute=lambda x: get_dt_iso_format_utc(x, 'last_update'),
            default='',
            readonly=True,
            required=False
        )
    }
)

pagination_parser = reqparse.RequestParser(bundle_errors=True)
pagination_parser.add_argument(
    'page',
    type=int,
    required=False,
    default=1,
    help='Page number'
)
pagination_parser.add_argument(
    'per_page',
    type=int,
    required=False,
    choices=[2, 10, 25, 50, 100],
    default=10,
    help='Results per page {error_msg}'
)

pagination_api_model = product_ns.model(
    'Pagination', {
        'page': fields.Integer(
            description='Number of this page of results',
            attribute='page'
        ),
        'total_pages': fields.Integer(
            description='Total number of pages of results',
            attribute='pages'
        ),
        'items_per_page': fields.Integer(
            description='Number of items per page of results',
            attribute='per_page'
        ),
        'total_items': fields.Integer(
            description='Total number of results',
            attribute='total'
        ),
        'items': fields.List(fields.Nested(product_api_model))
    }
)
