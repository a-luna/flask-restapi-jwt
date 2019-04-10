"""This module provides methods to generate and retrieve RSA keys used to sign and verify auth_tokens."""
from pathlib import Path

from flask import current_app
from Cryptodome.PublicKey import RSA

from app.util.result import Result


APP_FOLDER = Path(__file__).resolve().parent.parent
STATIC_FOLDER = APP_FOLDER / "static"
PUBLIC_KEY_FILENAME = "public.pem"


def generate_new_key(key_size=2048):
    """Generate a new RSA key for public key encryption of auth tokens.

    This function generates a new RSA key and outputs the RSA parameters of the key
    to the terminal. The output can be directly copied and pasted into the .env file
    in the project root, making the values available as environment variables. If
    the .env file does not contain any RSA parameters, JWT auth tokens will be encoded
    using the SECRET_KEY environment variable/flask app config value.

    For reference, the meaning of the RSA parameters is given below:
        key.n = modulus
        key.e = public_exponent
        key.d = private_exponent
        key.p = first_prime_number
        key.q = second_prime_number
        key.u = q_inv_crt
    """
    try:
        key = RSA.generate(key_size)
        print("Add the entries below to your .env file:\n")
        print(f'JWT_KEY_N="{key.n}"')
        print(f'JWT_KEY_E="{key.e}"')
        print(f'JWT_KEY_D="{key.d}"')
        print(f'JWT_KEY_P="{key.p}"')
        print(f'JWT_KEY_Q="{key.q}"')
        print(f'JWT_KEY_U="{key.u}"')
        return Result.Ok(key)
    except Exception as e:
        error = f"Error: {repr(e)}"
        return Result.Fail(error)


def create_public_key_file(static_folder=STATIC_FOLDER):
    """Create public.pem file in static folder.

    You should create a new public.pem file whenever you change the RSA key values stored
    in the .env file. The public.pem file is used by external services to verify the
    integrity of auth tokens issued by this service. If the public.pem file is not updated
    when RSA key values change, external services will consider auth tokens to be invalid since
    decoding will produce an InvalidTokenError.
    """
    result = get_public_key()
    if result.failure:
        return result
    public_key = result.value
    public_key_file = static_folder / PUBLIC_KEY_FILENAME
    try:
        if public_key_file.exists():
            public_key_file.unlink()
        public_key_file.write_bytes(public_key)
        return Result.Ok()
    except Exception as e:
        error = f"Error occurred creating public key file. Details:\n{repr(e)}"
        return Result.Fail(error)


def get_private_key():
    """Return RSA key in PEM format used to sign auth tokens."""
    result = _construct_rsa_key()
    if result.failure:
        return result
    key = result.value
    private_key = key.export_key()
    return Result.Ok(private_key)


def get_public_key():
    """Return RSA key in PEM format used to verify auth tokens."""
    result = _construct_rsa_key()
    if result.failure:
        return result
    key = result.value
    public_key = key.publickey().export_key()
    return Result.Ok(public_key)


def _construct_rsa_key():
    key_n = current_app.config.get("JWT_KEY_N")
    key_e = current_app.config.get("JWT_KEY_E")
    key_d = current_app.config.get("JWT_KEY_D")
    key_p = current_app.config.get("JWT_KEY_P")
    key_q = current_app.config.get("JWT_KEY_Q")
    key_u = current_app.config.get("JWT_KEY_U")
    if (
        key_n is None
        or key_e is None
        or key_d is None
        or key_p is None
        or key_q is None
        or key_u is None
    ):
        error = "One or more required key values not found, unable to construct RSA encryption key."
        return Result.Fail(error)
    try:
        key_tuple = (
            int(key_n),
            int(key_e),
            int(key_d),
            int(key_p),
            int(key_q),
            int(key_u),
        )
    except ValueError as e:
        error = f"Error occurred converting key value to integer, details:\n{repr(e)}"
        return Result.Fail(error)
    key = RSA.construct(key_tuple)
    return Result.Ok(key)
