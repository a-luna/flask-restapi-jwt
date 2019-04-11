"""API and API namespace configuration."""
from pathlib import Path

from Cryptodome.PublicKey import RSA

from flask import Blueprint
from flask_restplus import Api

APP_FOLDER = Path(__file__).resolve().parent.parent
PUBLIC_KEY_FILE = APP_FOLDER / "static" / "public.pem"
public_key = (
    RSA.import_key(PUBLIC_KEY_FILE.read_bytes())
    .publickey()
    .export_key()
    .decode("utf-8")
)

API_DESCRIPTION = (
    "<p>API methods marked with a lock icon require that a valid authorization "
    "token is sent in the header of any request. If a request is sent without "
    "authorization, the response will be <strong>401 UNAUTHORIZED</strong>. "
    "Follow the steps below to issue a new token and to include the token in "
    "your requests:</p>"
    "<ol><li>Register a new user with the "
    '<strong><span style="color:#49cc90">POST /auth/register</span></strong> '
    "method (or login with an existing user with the "
    '<strong><span style="color:#49cc90">POST /auth/login</span></strong> method)'
    '<p style="margin: 5px 0;font-weight:700"><i>After successful registration or '
    "login, the API will issue an authorization token and send the token in the "
    "<u>Authorization</u> field of the response.</i></p></li>"
    '<li style="margin: 0 0 5px">Copy the JWT value and click the '
    '<strong><span style="color:#49cc90">Authorize</span></strong> button below '
    "these instructions.</li>"
    '<li style="margin: 0 0 5px">In the <strong>Available Authorizations</strong> '
    "box that appears, paste the JWT value into the <strong>Value</strong> textbox "
    'and click <strong><span style="color:#49cc90">Authorize</span></strong>.</li>'
    '<li style="margin: 0 0 5px">Click <strong>Close</strong> to close the '
    "<strong>Available Authorizations</strong> box.</li>"
    "<li>All the lock icons should change from being unlocked to locked. This "
    "indicates that the authorization token will be sent in the header of "
    "any request made to the API."
    '<p style="margin: 5px 0;font-weight:700"><i>Authorization token is valid '
    "for 15 minutes after being issued. Also, token will be blacklisted and "
    "invlidated after using the</i> "
    '<strong><span style="color:#49cc90">POST /auth/logout</span></strong> '
    "<i>method. You can always generate a new token by logging in with valid "
    "user credentials.</i></p></li></ol>"
    "<p>The auth token contains a signature which was generated with RSA "
    "public-key cryptography. You can verify the integrity of any auth token with "
    "this public key:</p>"
    f'<div><pre style="width:min-content;margin:0 auto;"><code>{public_key}</code></pre></div>'
    "<p>Please note that some API methods require a valid authorization "
    "token AND administrator privileges. These methods are: "
    '<strong><span style="color:#49cc90">POST product/{name}</span></strong>, '
    '<strong><span style="color:#fca130">PUT product/{name}</span></strong> and '
    '<strong><span style="color:#f93e3e">DELETE product/{name}</span></strong>. '
    "Regular users can use all <strong>/auth</strong> methods, as well as "
    '<strong><span style="color:#61affe">GET /product</span></strong> '
    ' and <strong><span style="color:#61affe">GET product/{name}</span></strong> '
    "methods. Administrator priveleges cannot be granted through this API.</p>"
    "<p>This API does not provide an actual service, this is a live demo of a "
    "boilerplate Flask-RESTPlus project, detailed in a post on "
    '<a href="https://www.alunablog.com" target="_blank">alunablog.com.</a></p>'
)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="1.0",
    title="Flask-RESTPlus API with JWT-Based Authentication",
    description=API_DESCRIPTION,
    doc="/ui",
    authorizations=authorizations,
)

from app.api.auth import auth_ns
from app.api.product import product_ns

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(product_ns, path="/product")
