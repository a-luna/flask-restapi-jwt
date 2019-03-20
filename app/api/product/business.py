from datetime import datetime
from http import HTTPStatus

from flask_restplus import abort

from app import db
from app.models.product import Product
from app.util.datetime_functions import DT_FORMAT_ISO


def retrieve_product(product_name):
    release_info = Product.find_by_name(product_name)
    if release_info:
        return release_info, HTTPStatus.OK
    else:
        error = f'{product_name} not found in database.'
        abort(HTTPStatus.NOT_FOUND, error, status='fail')


def create_product(data):
    product_name = data['product_name']
    exists = Product.find_by_name(product_name)
    if exists:
        error = f'Product name: {product_name} already exists, must be unique.'
        abort(HTTPStatus.CONFLICT, error, status='fail')
    try:
        product_dict = {}
        for k, v in data.items():
            if k is not 'Authorization':
                product_dict[k] = v
        product_dict['last_update'] = datetime.utcnow()
        new_product = Product(**product_dict)
        db.session.add(new_product)
        db.session.commit()
        response_object = dict(
            status='success',
            message=f'New product added: {product_name}.',
            location=f'/api/product/{product_name}')
        return response_object, HTTPStatus.CREATED
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')


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
        product_data = dict(
            product_name=updated.product_name,
            release_info_url=updated.release_info_url,
            xpath_version_number=updated.xpath_version_number,
            xpath_download_url=updated.xpath_download_url,
            newest_version_number=updated.newest_version_number,
            download_url=updated.download_url,
            last_update=updated.last_update_utc_iso,
            last_checked=updated.last_checked_utc_iso)
        response_data = dict(
            status='success',
            data=product_data)
        return response_data, HTTPStatus.OK
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')


def delete_product(product_name):
    release_info = Product.find_by_name(product_name)
    if not release_info:
        return '', HTTPStatus.NO_CONTENT

    try:
        db.session.delete(release_info)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')
