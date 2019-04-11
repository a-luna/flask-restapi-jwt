"""This module provides methods to generate and retrieve RSA keys used to sign and verify auth_tokens."""
from pathlib import Path

from flask import current_app
from Cryptodome.PublicKey import RSA

from app.util.result import Result
from create_pem import construct_rsa_key


def get_private_key():
    """Return RSA key used to sign auth tokens in PEM format."""
    result = construct_rsa_key()
    if not result["success"]:
        return Result.Fail(result["error"])
    key = result["value"]
    private_key = key.export_key()
    return Result.Ok(private_key)


def get_public_key():
    """Return RSA key used to verify auth tokens in PEM format."""
    result = construct_rsa_key()
    if not result["success"]:
        return Result.Fail(result["error"])
    key = result["value"]
    public_key = key.publickey().export_key()
    return Result.Ok(public_key)
