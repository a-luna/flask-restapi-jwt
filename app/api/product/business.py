from datetime import datetime, timezone

from flask import url_for, jsonify
from flask_restplus import abort

from app import db
from app.models.product import Product
from app.util.datetime_functions import (
    convert_dt_for_display, convert_dt_to_user_tz_str, DT_FORMAT_ISO
)


def retrieve_product(product_name):
    release_info = Product.find_by_name(product_name)
    if release_info:
        return release_info, 200
    else:
        abort(404, f'{product_name} not found in database.', status='fail')


def create_product(data):
    product_name = data['product_name']
    exists = Product.find_by_name(product_name)
    if exists:
        response_object = {
            'status': 'fail',
            'message': f'Product name: {product_name} already exists, must be '
            'unique.'
        }
        return response_object, 409
    try:
        product_dict = {}
        for k, v in data.items():
            if k is not 'Authorization':
                product_dict[k] = v
        product_dict['last_update'] = datetime.utcnow()
        new_product = Product(**product_dict)
        db.session.add(new_product)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'New product added: {product_name}.',
            'location': f'/api/product/{product_name}'
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Error: {}.'.format(repr(e))
        }
        return response_object, 500


def update_product(product_name, data):
    request_data = {k:v for k,v in data.items()}
    updated = Product.find_by_name(product_name)
    if not updated:
        request_data['product_name'] = product_name
        return create_product(request_data)
    try:
        for k, v in request_data.items():
            setattr(updated, k, v)
        setattr(updated, 'last_update', datetime.utcnow())
        db.session.commit()
        response_object = {
            'status': 'success',
            'data': {
                'product_name': updated.product_name,
                'release_info_url': updated.release_info_url,
                'xpath_version_number': updated.xpath_version_number,
                'xpath_download_url': updated.xpath_download_url,
                'newest_version_number': updated.newest_version_number,
                'download_url': updated.download_url,
                'last_update': updated.last_update_utc_iso,
                'last_checked': updated.last_checked_utc_iso}}
        return response_object, 200
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Error: {}.'.format(repr(e))
        }
        return response_object, 500


def delete_product(product_name):
    release_info = Product.find_by_name(product_name)
    if not release_info:
        return '', 204

    try:
        db.session.delete(release_info)
        db.session.commit()
        return '', 204
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Error: {}.'.format(repr(e))
        }
        return response_object, 500
