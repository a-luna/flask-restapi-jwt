"""API endpoint definitions for /product namespace."""
from http import HTTPStatus

from flask_restplus import Resource

from app.api.auth.decorator import admin_token_required
from app.api.product import product_ns
from app.api.product.business import (
    retrieve_product,
    create_product,
    update_product,
    delete_product,
)
from app.api.product.dto import (
    post_product_parser,
    put_product_parser,
    pagination_parser,
    product_overview,
    product_detail,
    pagination_api_model,
)
from app.models.product import Product as ProductModel


@product_ns.route("/")
@product_ns.doc(responses={HTTPStatus.BAD_REQUEST: "Validation error."})
class ProductList(Resource):
    """Handlers for HTTP requests to /product API endpoints."""

    @product_ns.doc("Get a list of all products.")
    @product_ns.expect(pagination_parser, validate=True)
    @product_ns.marshal_with(
        pagination_api_model,
        code=HTTPStatus.OK,
        description="Successfully retrieved product list.",
    )
    def get(self):
        """Get a list of all products."""
        args = pagination_parser.parse_args()
        return ProductModel.query.paginate(
            args.get("page", 1), args.get("per_page", 10), error_out=False
        )

    @product_ns.doc(
        "Add new product.",
        security="Bearer",
        responses={
            HTTPStatus.CREATED: "Product was added.",
            HTTPStatus.UNAUTHORIZED: "Please login with a valid authorization token.",
            HTTPStatus.FORBIDDEN: "You are not authorized to perform the requested action.",
            HTTPStatus.CONFLICT: "Product name already exists, must be unique.",
            HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error.",
        },
    )
    @product_ns.expect(post_product_parser, validate=True)
    @admin_token_required
    def post(self):
        """Add new product."""
        args = post_product_parser.parse_args()
        return create_product(data=args)


@product_ns.route("/<name>")
@product_ns.param("name", "Product name")
@product_ns.doc(responses={HTTPStatus.BAD_REQUEST: "Validation error."})
class Product(Resource):
    """Handlers for HTTP requests to /product/{name} API endpoints."""

    @product_ns.doc(
        "Retrieve a product.", responses={HTTPStatus.NOT_FOUND: "Product not found."}
    )
    @product_ns.marshal_with(
        product_overview,
        code=HTTPStatus.OK,
        description="Successfully retrieved product.",
    )
    def get(self, name):
        """Retrieve a product."""
        return retrieve_product(name)

    @product_ns.doc(
        "Update an existing product.",
        security="Bearer",
        responses={
            HTTPStatus.OK: "Product was updated.",
            HTTPStatus.UNAUTHORIZED: "Please login with a valid authorization token.",
            HTTPStatus.FORBIDDEN: "You are not authorized to perform the requested action.",
            HTTPStatus.NOT_FOUND: "Product not found",
            HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error.",
        },
    )
    @product_ns.expect(put_product_parser, validate=True)
    @product_ns.marshal_with(
        product_detail,
        code=HTTPStatus.OK,
        description="Successfully retrieved product.",
    )
    @admin_token_required
    def put(self, name):
        """Update an existing product."""
        args = put_product_parser.parse_args()
        return update_product(product_name=name, data=args)

    @product_ns.doc(
        "Delete a product.",
        security="Bearer",
        responses={
            HTTPStatus.NO_CONTENT: "Product was deleted.",
            HTTPStatus.UNAUTHORIZED: "Please login with a valid authorization token.",
            HTTPStatus.FORBIDDEN: "You are not authorized to perform the requested action.",
        },
    )
    @admin_token_required
    def delete(self, name):
        """Delete a product."""
        return delete_product(name)
