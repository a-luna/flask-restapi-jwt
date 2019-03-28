"""Create and configure API object and initialize API namespaces."""
from flask import Blueprint
from flask_restplus import Api


_API_DESCRIPTION = (
    'This API does not provide any actual service, this is a live demo of a '
    'boilerplate Flask-RESTPlus project, detailed in a post on alunablog.com. '
    'The API is fully functional, however some operations require administrator '
    'access which cannot be granted through the API. After registering a new '
    'user or after a successful login, the JSON response will contain a field '
    'named "Authorization". This field contains an encoded JSON web token '
    'with the ID of the user and the token expiration time. You should copy '
    'this value because any method marked with a lock icon requires a '
    'authorization token. However, only normal users can be created through '
    'this API, admin users can not be created. Because of this, creating, '
    'updating and deleting products can only be performed by admin users. '
    'Regular users can use all "auth" functions, GET "/product" and GET '
    '"product/{name}" methods. If a regular user attempts to create, update '
    'or modify a product the API response will be HTTPStatus.UNAUTHORIZED (401) '
    'with message "You are not authorized to perform the requested action."'
)

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    api_bp,
    version='1.0',
    title='Flask-RESTPlus API with JWT-Based Authentication',
    description=_API_DESCRIPTION,
    doc='/ui'
)


from app.api.auth import auth_ns
from app.api.product import product_ns

api.add_namespace(auth_ns)
api.add_namespace(product_ns, path='/product')