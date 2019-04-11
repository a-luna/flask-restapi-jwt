"""Bootstrap script to create public key file before initializing flask app."""
import os
from pathlib import Path

from Cryptodome.PublicKey import RSA

APP_ROOT = Path(__file__).resolve().parent
PUBLIC_KEY_FILE = APP_ROOT / "app" / "static" / "public.pem"


def construct_rsa_key():
    """Construct RSA key from parameter values stored in environment variables."""
    key_n = os.getenv("JWT_KEY_N")
    key_e = os.getenv("JWT_KEY_E")
    key_d = os.getenv("JWT_KEY_D")
    key_p = os.getenv("JWT_KEY_P")
    key_q = os.getenv("JWT_KEY_Q")
    key_u = os.getenv("JWT_KEY_U")
    if (
        key_n is None
        or key_e is None
        or key_d is None
        or key_p is None
        or key_q is None
        or key_u is None
    ):
        error = "One or more required key values not found, unable to construct RSA encryption key."
        return dict(success=False, error=error)

    try:
        key_tuple = (
            int(key_n),
            int(key_e),
            int(key_d),
            int(key_p),
            int(key_q),
            int(key_u),
        )
        key = RSA.construct(key_tuple)
        return dict(success=True, value=key)
    except ValueError as e:
        error = f"Error occurred converting key value to integer, details:\n{repr(e)}"
        return dict(success=False, error=error)


def create_public_key_file():
    """Create public key file in PEM format."""
    result = construct_rsa_key()
    if not result["success"]:
        return result
    key = result["value"]
    public_key = key.publickey().export_key()
    try:
        if PUBLIC_KEY_FILE.exists():
            PUBLIC_KEY_FILE.unlink()
        PUBLIC_KEY_FILE.write_bytes(public_key)
        print(f"Successfully created public key file at:\n{PUBLIC_KEY_FILE}")
        return dict(success=True)
    except Exception as e:
        error = f"Error occurred creating public key file. Details:\n{repr(e)}"
        return dict(success=False, error=error)


if __name__ == "__main__":
    result = create_public_key_file()
    if not result["success"]:
        print(result["error"])
