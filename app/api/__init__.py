"""Create and configure API object and initialize API namespaces."""
from flask import Blueprint
from flask_restplus import Api


_API_DESCRIPTION = (
    'This free API provides the newest version number and download URL for '
    'popular software packages and libraries. The idea for this API was '
    'driven by the need to repeatedly update bash scripts that contain '
    'hardcoded references to a version number or download URL. Now, instead '
    'of hardcoding these values, they can be retrieved from this API and '
    'scripts never have to be updated when a new version is released. To do '
    'so, send a GET request with the name of a software package (using curl, '
    'httpie or similar tool), then parse the JSON response (using JQ or '
    'similar tool) which contains the newest version number of the product '
    'and a download URL for the newest version. Version information for each '
    'product is updated every 60 minutes.'
)

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    api_bp,
    version='1.0',
    title='Newest Version API',
    description=_API_DESCRIPTION,
    doc='/ui'
)


from app.api.auth import auth_ns
from app.api.product import product_ns

api.add_namespace(auth_ns)
api.add_namespace(product_ns, path='/product')