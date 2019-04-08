import os

from Cryptodome.PublicKey import RSA


def get_private_key():
    key = construct_rsa_key()
    return key.export_key()


def get_public_key():
    key = construct_rsa_key()
    return key.publickey().export_key()


def construct_rsa_key():
    key_n = os.getenv("JWT_KEY_N")
    key_e = os.getenv("JWT_KEY_E")
    key_d = os.getenv("JWT_KEY_D")
    key_p = os.getenv("JWT_KEY_P")
    key_q = os.getenv("JWT_KEY_Q")
    key_u = os.getenv("JWT_KEY_U")
    key_tuple = (int(key_n), int(key_e), int(key_d), int(key_p), int(key_q), int(key_u))
    return RSA.construct(key_tuple)
