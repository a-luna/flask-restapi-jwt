"""Parsers and serializers for /auth API endpoints."""
import re
from flask_restplus import fields, reqparse
from flask_restplus.reqparse import Argument
from flask_restplus.inputs import email

from app.api.auth import auth_ns


B64_REGEX = re.compile(r"^[A-Za-z0-9+/=]+$")


def base64_standard(input):
    """Return input if input is b64 encoded string, raise an exception if validation fails."""
    b64_encoded = B64_REGEX.match(input)
    total_chunks, extra_digits = divmod(len(input), 4)
    if b64_encoded and total_chunks and not extra_digits:
        return input
    else:
        raise ValueError("Value must be a base64 encoded string")


secure_reqparser = reqparse.RequestParser(bundle_errors=True)
secure_reqparser.add_argument(
    name="key",
    type=base64_standard,
    required=True,
    nullable=False,
    help="Encrypted session key.",
)
secure_reqparser.add_argument(
    name="iv",
    type=base64_standard,
    required=True,
    nullable=False,
    help="Initialization vector.",
)
secure_reqparser.add_argument(
    name="ct", type=base64_standard, required=True, nullable=False, help="Ciphertext"
)

auth_reqparser = reqparse.RequestParser(bundle_errors=True)
auth_reqparser.add_argument(
    name="email",
    type=email(),
    location="form",
    required=True,
    nullable=False,
    help="User email address.",
)
auth_reqparser.add_argument(
    name="password",
    type=str,
    location="form",
    required=True,
    nullable=False,
    help="User password.",
)

user_model = auth_ns.model(
    "User",
    {
        "email": fields.String,
        "public_id": fields.String,
        "admin": fields.Boolean,
        "registered_on": fields.String(attribute="registered_on_str"),
    },
)
