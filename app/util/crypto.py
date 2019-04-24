"""This module provides methods to generate and retrieve RSA keys used to sign and verify auth_tokens."""
import json
import re
from base64 import standard_b64decode, standard_b64encode

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad

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


def get_public_key_hex():
    """Return RSA public key in PEM format without header and footer."""
    result = get_public_key()
    if result.failure:
        return result
    public_key = result.value
    split = public_key.split(b"\n")
    public_key_b64 = b"".join(split[1 : len(split) - 1])
    public_key_bytes = standard_b64decode(public_key_b64)
    return Result.Ok(public_key_bytes.hex())


def encrypt_user_credentials(email, password):
    result = construct_rsa_key()
    if not result["success"]:
        return Result.Fail(result["error"])
    key = result["value"]
    public_key = key.publickey()
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    encrypted_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_CBC)
    plaintext = f"{email}:{password}"
    ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))

    key = standard_b64encode(encrypted_key).decode("utf-8")
    iv = standard_b64encode(cipher_aes.iv).decode("utf-8")
    ct = standard_b64encode(ciphertext).decode("utf-8")
    enc_user_creds = dict(key=key, iv=iv, ct=ct)
    return Result.Ok(enc_user_creds)


def decrypt_user_credentials(encoded_key, encoded_iv, encoded_ct):
    encrypted_key = standard_b64decode(encoded_key)
    iv = standard_b64decode(encoded_iv)
    ciphertext = standard_b64decode(encoded_ct)
    result = get_private_key()
    if result.failure:
        return result
    private_key = RSA.import_key(result.value)
    cipher_rsa = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    try:
        session_key = cipher_rsa.decrypt(encrypted_key)
        cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
        creds_plaintext = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)
    except KeyError as e:
        error = f"Decryption Error: {repr(e)}"
        return Result.Fail(error)
    except ValueError as e:
        error = f"Decryption Error: {repr(e)}"
        return Result.Fail(error)

    split = creds_plaintext.decode("ascii").split(":")
    if len(split) != 2:
        error = 'User credentials not formatted correctly, expected 2 strings separated by ":" char.'
        return Result.Fail(error)
    user_creds = dict(email=split[0], password=split[1])
    return Result.Ok(user_creds)
