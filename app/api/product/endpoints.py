"""API endpoint definitions for /product namespace."""
from flask import request
from flask_restplus import Resource

from app.api.auth.decorator import admin_token_required
from app.api.product import product_ns
from app.api.product.business import (
    retrieve_product, create_product, update_product, delete_product
)
from app.api.product.dto import (
    post_product_parser, put_product_parser, delete_product_parser,
    pagination_parser, product_api_model, pagination_api_model,
)
from app.models.product import Product as ProductModel


@product_ns.route("/")
@product_ns.doc(responses={400: "Validation error."})
class ProductList(Resource):
    "Handlers for HTTP requests to /product API endpoints."

    @product_ns.doc(
        "Get a list of all products.",
        parser=pagination_parser,
        validate=True,
        responses={200: "Successfully retrieved product list."})
    @product_ns.marshal_with(pagination_api_model)
    def get(self):
        """Get a list of all products."""
        return ProductModel.query.paginate(
            request.form.get("page", 1),
            request.form.get("per_page", 10),
            error_out=False
        )

    @product_ns.doc(
        "Add new product.",
        security="Bearer",
        parser=post_product_parser,
        validate=True,
        responses={
            201: "Product successfully added.",
            401: "Admin token required.",
            409: "Product name already exists, must be unique.",
            500: "Internal server error."})
    @admin_token_required
    def post(self):
        """Add new product."""
        v = request
        args = post_product_parser.parse_args()
        return create_product(data=args)


@product_ns.route("/<name>")
@product_ns.param("name", "Product name")
@product_ns.doc(responses={400: "Validation error."})
class Product(Resource):
    "Handlers for HTTP requests to /product/{name} API endpoints."

    @product_ns.doc(
        "Retrieve a product.",
        responses={
            200: "Successfully retrieved product.",
            404: "Product not found.",})
    @product_ns.marshal_with(product_api_model)
    def get(self, name):
        """Retrieve a product."""
        return retrieve_product(name)

    @product_ns.doc(
        "Update an existing product.",
        security="Bearer",
        parser=put_product_parser,
        validate=True,
        responses={
            200: "Successfully updated product.",
            201: "Product successfully added.",
            401: "Admin token required.",
            500: "Internal server error."})
    @admin_token_required
    def put(self, name):
        """Update an existing product."""
        return update_product(product_name=name, data=request.form)

    @admin_token_required
    @product_ns.doc(
        "Delete a product.",
        security="Bearer",
        parser=delete_product_parser,
        validate=True,
        responses={
            204: "Successfully deleted product.",
            401: "Operation requires administrator access, please login.",
            500: "Internal server error."})
    def delete(self, name):
        """Delete a product."""
        return delete_product(name)
