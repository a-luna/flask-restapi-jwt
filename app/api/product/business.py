from datetime import datetime
from http import HTTPStatus

from flask_restplus import abort

from app import db
from app.models.product import Product


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
            product_dict[k] = v
        product_dict['last_update'] = datetime.utcnow()
        new_product = Product(**product_dict)
        db.session.add(new_product)
        db.session.commit()
        response_object = dict(
            status='success',
            message=f'New product added: {product_name}.',
            location=f'/api/v1/product/{product_name}')
        return response_object, HTTPStatus.CREATED
    except Exception as e:
        error = f'Error: {repr(e)}'
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status='fail')


def update_product(product_name, data):
    request_data = {k:v for k,v in data.items()}
    update_product = Product.find_by_name(product_name)
    if not update_product:
        error = f'Product name: {product_name} not found.'
        abort(HTTPStatus.NOT_FOUND, error, status='fail')
    try:
        for k, v in request_data.items():
            setattr(update_product, k, v)
        setattr(update_product, 'last_update', datetime.utcnow())
        db.session.commit()
        product_data = dict(
            product_name=update_product.product_name,
            release_info_url=update_product.release_info_url,
            xpath_version_number=update_product.xpath_version_number,
            xpath_download_url=update_product.xpath_download_url,
            newest_version_number=update_product.newest_version_number,
            download_url=update_product.download_url,
            last_update=update_product.last_update_str,
            last_checked=update_product.last_checked_str)
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
