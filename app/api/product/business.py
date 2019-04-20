"""Business logic for /product API endpoints."""
from datetime import datetime
from http import HTTPStatus

from flask import jsonify
from flask_restplus import abort

from app import db
from app.models.product import Product


def retrieve_product(product_name):
    release_info = Product.find_by_name(product_name)
    if release_info:
        return release_info, HTTPStatus.OK
    else:
        error = f"{product_name} not found in database."
        abort(HTTPStatus.NOT_FOUND, error, status="fail")


def create_product(data):
    product_name = data["product_name"]
    exists = Product.find_by_name(product_name)
    if exists:
        error = f"Product name: {product_name} already exists, must be unique."
        abort(HTTPStatus.CONFLICT, error, status="fail")
    try:
        product_dict = {}
        for k, v in data.items():
            product_dict[k] = v
        product_dict["last_update"] = datetime.utcnow()
        new_product = Product(**product_dict)
        db.session.add(new_product)
        db.session.commit()
        response_object = dict(
            status="success", message=f"New product added: {product_name}."
        )
        response = jsonify(response_object)
        response.status_code = HTTPStatus.CREATED
        response.headers["Location"] = f"/api/v1/product/{product_name}"
        return response
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")


def update_product(product_name, data):
    request_data = {k: v for k, v in data.items()}
    update_product = Product.find_by_name(product_name)
    if not update_product:
        error = f"Product name: {product_name} not found."
        abort(HTTPStatus.NOT_FOUND, error, status="fail")
    try:
        for k, v in request_data.items():
            setattr(update_product, k, v)
        setattr(update_product, "last_update", datetime.utcnow())
        db.session.commit()
        return update_product, HTTPStatus.OK
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")


def delete_product(product_name):
    release_info = Product.find_by_name(product_name)
    if not release_info:
        return "", HTTPStatus.NO_CONTENT

    try:
        db.session.delete(release_info)
        db.session.commit()
        return "", HTTPStatus.NO_CONTENT
    except Exception as e:
        error = f"Error: {repr(e)}"
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, error, status="fail")
