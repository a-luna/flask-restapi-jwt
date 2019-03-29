"""Create and configure API object and initialize API namespaces."""
from flask import Blueprint
from flask_restplus import Api


_API_DESCRIPTION = (
    '<p>This API does not provide an actual service, this is a live demo of a '
    'boilerplate Flask-RESTPlus project, detailed in a post on '
    '<a href="https://www.alunablog.com" target="_blank">alunablog.com.</a></p>'
    '<p>The API is fully functional, however some operations require administrator '
    'access which cannot be granted through the API. After registering a new user '
    'or after a successful login, the JSON response will contain a field named '
    '<strong>Authorization</strong>. This field contains an encoded JSON web token '
    'with the ID of the user and the token expiration time. You should copy this '
    'value because any method marked with a lock icon requires a valid authorization '
    'token. However, some API endpoints require a valid authorization token AND '
    'administrator privileges. These endpoints are: <strong>POST</strong>, '
    '<strong>PUT</strong> and <strong>DELETE</strong> <strong>product/{name}</strong>. '
    'Regular users can use all <strong>/auth</strong> endpoints, as well as '
    '<strong>GET</strong> <strong>/product</strong> and <strong>GET</strong> '
    '<strong>product/{name}</strong> endpoints.</p>'
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