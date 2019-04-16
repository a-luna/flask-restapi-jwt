"""API and API namespace configuration."""
from pathlib import Path

from Cryptodome.PublicKey import RSA

from flask import Blueprint
from flask_restplus import Api

APP_FOLDER = Path(__file__).resolve().parent.parent
PUBLIC_KEY_FILE = APP_FOLDER / "static" / "public.pem"

if PUBLIC_KEY_FILE.exists():
    public_key = PUBLIC_KEY_FILE.read_bytes().decode("ascii")
else:
    public_key = "Error occurred locating public key file, auth tokens will be \nsigned using HS256 algorithm rather than with RS256 public-key \ncrypto algorithm."
public_key_css = "width:min-content;background:rgba(0,0,0,.05);border:1px solid rgba(59,65,81,.3);border-radius:4px;margin:0 auto;padding:5px 10px;white-space:normal"
h2_style = "color:#9012fe;font-size:1em;margin:1em 0 0"

API_DESCRIPTION = (
    f'<h2 style="{h2_style}">What is the purpose of this API? What service does it '
    "provide?</h2>"
    "<p>This API does not provide an actual service, this is a live demo of "
    '<a href="https://www.alunablog.com" target="_blank">a boilerplate '
    "Flask-RESTPlus project</a> that demonstrates how to secure an API "
    "with Javascript Web Tokens (JWT).</p>"
    f'<h2 style="{h2_style}">Which methods require Authorization? Which methods '
    "are restricted to users with administrator access?</h2>"
    '<ul><li style="margin:0 0 0.5em">API methods marked with a lock icon require '
    "that a valid authorization token is sent in the header of any request. If a "
    "request is sent without an auth token or with an expired/invalid auth token, "
    "the status code of the response will be <strong>401 UNAUTHORIZED</strong>.</li>"
    '<li style="margin:0 0 0.5em">Some API methods require a valid authorization '
    "token AND administrator privileges. These methods are: "
    '<strong><span style="color:#49cc90">POST product/{name}</span></strong>, '
    '<strong><span style="color:#fca130">PUT product/{name}</span></strong> and '
    '<strong><span style="color:#f93e3e">DELETE product/{name}</span></strong>. '
    "If a user without administrator access sends a request containing a valid "
    "authorization token to any of these methods, the status code of the response "
    "will be <strong>403 FORBIDDEN</strong>.</li>"
    '<li style="margin:0 0 0.5em">Regular users can use all <strong>/auth</strong> '
    "methods, as well as "
    '<strong><span style="color:#61affe">GET /product</span></strong> '
    ' and <strong><span style="color:#61affe">GET product/{name}</span></strong> '
    "methods. Administrator priveleges cannot be granted through this API.</li></ul>"
    f'<h2 style="{h2_style}">How do I create an authorization token?</h2>'
    "<p>Auth tokens are issued by the API whenever a user logs in with valid "
    "credentials or when a user registers a new account with a unique email "
    "address. Follow the steps below to include an authorization token in the "
    "header of your requests:</p>"
    '<ol><li>Use the <a href="../../secure_auth">Secure Authorization</a> form '
    "to register a new user account or login as an existing user."
    '<p style="margin: 5px 0;font-weight:700"><i>After successful registration or '
    "login, you will receive an authorization token (the token is a base64-encoded "
    "string in JWT format). Copy the JWT value and return to this page by clicking "
    "on the <strong>API Docs</strong> link in the top-right corner.</i></p></li>"
    '<li style="margin: 0 0 5px">Click the '
    '<strong><span style="color:#49cc90">Authorize</span></strong> button below '
    "these instructions to open the <strong>Available Authorizations</strong> box.</li>"
    '<li style="margin: 0 0 5px">In the box that appears, paste the JWT value into '
    "the <strong>Value</strong> textbox and click "
    '<strong><span style="color:#49cc90">Authorize</span></strong>.</li>'
    '<li style="margin: 0 0 5px">Click <strong>Close</strong> to close the '
    "<strong>Available Authorizations</strong> box.</li>"
    "<li>All the lock icons should change from being unlocked to locked. This "
    "indicates that the authorization token will be sent in the header of "
    "any request made to the API."
    '<p style="margin: 5px 0;font-weight:700"><i>Each authorization token is valid '
    "for 15 minutes after being issued. Also, token will be blacklisted and "
    "invlidated after using the</i> "
    '<strong><span style="color:#49cc90">POST /auth/logout</span></strong> '
    "<i>method. You can always generate a new token with the "
    '<a href="../../secure_auth">Secure Authorization</a> form.</i></p></li></ol>'
    "<p>The auth token contains a signature which was generated with RSA "
    "public-key cryptography. You can verify the integrity of any auth token with "
    "this public key:</p>"
    f'<pre style="{public_key_css}"><code style="background:None">{public_key}</code></pre>'
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
