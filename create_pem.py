"""Bootstrap script to create public key file before initializing flask app."""
import os
from pathlib import Path

from Cryptodome.PublicKey import RSA

APP_ROOT = Path(__file__).resolve().parent
PUBLIC_KEY_FILE = APP_ROOT / "app" / "static" / "public.pem"


if __name__ == "__main__":
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
        print(error)

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
        print(error)

    key = RSA.construct(key_tuple)
    public_key = key.publickey().export_key()
    try:
        if PUBLIC_KEY_FILE.exists():
            PUBLIC_KEY_FILE.unlink()
        PUBLIC_KEY_FILE.write_bytes(public_key)
        print(f"Successfully created public key file at:\n{PUBLIC_KEY_FILE}")
    except Exception as e:
        error = f"Error occurred creating public key file. Details:\n{repr(e)}"
        print(error)
