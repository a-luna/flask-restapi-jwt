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
    public_key = "Error occurred locating public key file, auth tokens will be \nsigned using HS256 algorithm rather than with public-key \ncryptography."

public_key_style = "width:min-content;background:rgba(0,0,0,.05);border:1px solid rgba(59,65,81,.3);border-radius:4px;margin:0 auto;padding:5px 10px;white-space:normal"
h2_style = "color:#9012fe;font-size:1em;font-weight:900;margin:1em 0 0"
responsive_style = "overflow-x: auto;overflow-y: hidden;width: auto;padding: 0.5em"

API_DESCRIPTION = (
    f'<h2 style="{h2_style}">What is the purpose of this API? What service does it '
    "provide?</h2>"
    "<p>This API does not provide an actual service, this is a live demo of "
    '<a href="https://www.alunablog.com" target="_blank">a boilerplate '
    "Flask-RESTPlus project</a> that demonstrates how to secure an API "
    "with JSON Web Tokens (JWT).</p>"
    f'<h2 style="{h2_style}">Which methods require Authorization?</h2>'
    "<p>API methods marked with a lock icon require that a valid authorization token "
    "is sent in the header of any request. If a request is sent without an auth token "
    "or with an expired/invalid auth token, the status code of the response will be "
    '<strong style="color:#f93e3e">401 UNAUTHORIZED</strong>.</p>'
    "<p>API methods that require a valid authorization token AND administrator "
    "privileges are:</p>"
    '<ul><li style="margin:0 0 5px 0"><strong>POST product/{name}</strong></li>'
    '<li style="margin:0 0 5px 0"><strong>PUT product/{name}</strong></li>'
    '<li style="margin:0 0 5px 0"><strong>DELETE product/{name}</strong></li></ul>'
    "<p>If a user without administrator access sends a request containing a valid "
    "authorization token to any of these methods, the status code of the response "
    'will be <strong style="color:#f93e3e">403 FORBIDDEN</strong>. Administrator '
    "priveleges cannot be granted through this API.</p>"
    "<p>Regular (non-admin) users can use all <strong>/auth</strong> methods, as well as "
    "<strong><span>GET /product</span></strong> and "
    "<strong><span>GET product/{name}</span></strong> methods.</p>"
    f'<h2 style="{h2_style}">How do I create an authorization token?</h2>'
    "<p>Auth tokens are issued by the API whenever a user logs in with valid "
    "credentials or when a user registers a new account with a unique email "
    "address. Follow the steps below to include an authorization token in the "
    "header of your requests:</p>"
    '<ol><li><span style="font-weight:700">Use the <a href="../../secure_auth">Secure Authorization</a> form '
    "to register a new user account or login as an existing user.</span>"
    '<p style="margin: 5px 0"><i>After successful registration or '
    "login, you will receive an authorization token (the token is a base64-encoded "
    "string in JWT format). Copy the JWT value and return to this page by clicking "
    "on the <strong>API Docs</strong> link in the top-right corner.</i></p></li>"
    '<li style="margin: 0 0 5px"><span style="font-weight:700">Click the '
    '<strong><span style="color:#49cc90">Authorize</span></strong> button below '
    "these instructions to open the <strong>Available Authorizations</strong> box.</span></li>"
    '<li style="margin: 0 0 5px"><span style="font-weight:700">In the box that appears, paste the JWT value into '
    "the <strong>Value</strong> textbox and click "
    '<strong><span style="color:#49cc90">Authorize</span></strong>.</span></li>'
    '<li style="margin: 0 0 5px"><span style="font-weight:700">Click <strong>Close</strong> to close the '
    "<strong>Available Authorizations</strong> box.</span></li>"
    '<li><span style="font-weight:700">All the lock icons should change from being unlocked to locked. Now, the '
    "authorization token will be sent in the header of any request made to the API.</span>"
    '<p style="margin: 5px 0"><i>Each authorization token is valid '
    "for 15 minutes after being issued. Also, a token will be blacklisted (invalidated) "
    "after using the</i> "
    '<strong><span style="color:#49cc90">POST /auth/logout</span></strong> '
    "<i>method. You can always generate a new token by logging in with the "
    '<a href="../../secure_auth">Secure Authorization</a> form.</i></p></li></ol>'
    f'<h2 style="{h2_style}">What algorithm is used to sign the authorization tokens?</h2>'
    "<p>Auth tokens are generated using a public-key signature to prevent any tampering. "
    "This also allows you or any other client to verify the authenticity of an auth token "
    "using the public-key below:</p>"
    f'<div style="{responsive_style}"><pre style="{public_key_style}">'
    f'<code style="background:None">{public_key}</code></pre></div>'
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
