"""Parsers and serializers for /product API endpoints."""
from flask_restplus import fields, reqparse
from flask_restplus.reqparse import Argument
from flask_restplus.inputs import URL

from app.api.product import product_ns
from app.util.regex import DB_NAME_PATTERN, DB_NAME_REGEX


def product_name(name):
    """Return name if valid, raise an excaption if validation fails."""
    if DB_NAME_REGEX.match(name):
        return name
    else:
        raise ValueError(
            f'"{name}" contains one or more invalid characters. Product name '
            'must contain only letters (a-z), numbers (0-9), "-" (hyphen '
            'character) and/or "_" (underscore character).')


def xpath_query(xpath):
    """Return xpath if valid, raise an excaption if validation fails."""
    if xpath and not xpath.isspace():
        return xpath
    else:
        raise ValueError('XPath query must not be null or empty string.')

post_product_parser = reqparse.RequestParser(bundle_errors=True)
post_product_parser.add_argument(
    name='product_name',
    dest='product_name',
    type=product_name,
    location='form',
    required=True,
    nullable=False,
    case_sensitive=False)
post_product_parser.add_argument(
    name='release_info_url',
    dest='release_info_url',
    type=URL(schemes=['http', 'https']),
    location='form',
    required=True,
    nullable=False)
post_product_parser.add_argument(
    name='xpath_version_number',
    dest='xpath_version_number',
    type=xpath_query,
    location='form',
    required=True,
    nullable=False)
post_product_parser.add_argument(
    name='xpath_download_url',
    dest='xpath_download_url',
    type=xpath_query,
    location='form',
    required=True,
    nullable=False)

put_product_parser = reqparse.RequestParser(bundle_errors=True)
put_product_parser.add_argument(
    name='release_info_url',
    dest='release_info_url',
    type=URL(schemes=['http', 'https']),
    location='form',
    required=False,
    nullable=False,
    store_missing=False)
put_product_parser.add_argument(
    name='xpath_version_number',
    dest='xpath_version_number',
    type=xpath_query,
    location='form',
    required=False,
    nullable=False,
    store_missing=False)
put_product_parser.add_argument(
    name='xpath_download_url',
    dest='xpath_download_url',
    type=xpath_query,
    location='form',
    required=False,
    nullable=False,
    store_missing=False)

product_api_model = product_ns.model(
    'Product', {
        'product_name': fields.String,
        'release_info_url': fields.String,
        'xpath_version_number': fields.String,
        'xpath_download_url': fields.String,
        'newest_version_number': fields.String,
        'download_url': fields.String,
        'last_update': fields.String(attribute='last_update_str'),
        'last_checked': fields.String(attribute='last_checked_str')},
        mask=('{'
            'product_name, '
            'newest_version_number, '
            'download_url, '
            'last_update, '
            'last_checked}'))

pagination_parser = reqparse.RequestParser(bundle_errors=True)
pagination_parser.add_argument(
    'page',
    type=int,
    required=False,
    default=1,
    help='Page number')
pagination_parser.add_argument(
    'per_page',
    type=int,
    required=False,
    choices=[5, 10, 25, 50, 100],
    default=10,
    help='Results per page {error_msg}')

pagination_api_model = product_ns.model(
    'Pagination', {
        'page': fields.Integer(attribute='page'),
        'total_pages': fields.Integer(attribute='pages'),
        'items_per_page': fields.Integer(attribute='per_page'),
        'total_items': fields.Integer(attribute='total'),
        'items': fields.List(fields.Nested(product_api_model))})
