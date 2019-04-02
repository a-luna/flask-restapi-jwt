"""Create and configure API object and initialize API namespaces."""
from flask import Blueprint
from flask_restplus import Api


_API_DESCRIPTION = (
    '<p>This API does not provide an actual service, this is a live demo of a '
    'boilerplate Flask-RESTPlus project, detailed in a post on '
    '<a href="https://www.alunablog.com" target="_blank">alunablog.com.</a></p>'
    '<p>After registering a new user or after a successful login, the response '
    'will contain a <strong>JSON Web Token (JWT)</strong> in a field named '
    '<strong>Authorization</strong>. In order to use any of the API methods that '
    'are marked with a lock icon, you must include this token with your request. '
    'To do so, copy the JWT value and click the '
    '<strong><span style="color:green">Authorize</span></strong> button below this '
    'paragraph to open the <strong>Available Authorizations</strong> box. Paste '
    'the token into the <strong>Value</strong> textbox and click '
    '<strong><span style="color:green">Authorize</span></strong>. Now, all the '
    'lock icons should change from being unlocked to locked. This indicates that '
    'the authorization token will be sent in the header of any request made to the '
    'API.</p><p>Please note that some API endpoints require a valid authorization '
    'token AND administrator privileges. These endpoints are: <strong>POST</strong>, '
    '<strong>PUT</strong> and <strong>DELETE</strong> <strong>product/{name}</strong>. '
    'Regular users can use all <strong>/auth</strong> endpoints, as well as '
    '<strong>GET</strong> <strong>/product</strong> and <strong>GET</strong> '
    '<strong>product/{name}</strong> endpoints.</p>')

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'}}

api = Api(
    api_bp,
    version='1.0',
    title='Flask-RESTPlus API with JWT-Based Authentication',
    description=_API_DESCRIPTION,
    doc='/ui',
    authorizations=authorizations)


from app.api.auth import auth_ns
from app.api.product import product_ns

api.add_namespace(auth_ns)
api.add_namespace(product_ns, path='/product')