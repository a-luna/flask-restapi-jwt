"""Unit tests for app.util.crypto module."""
import io
import sys
import unittest
from http import HTTPStatus
from pathlib import Path

from flask_testing import TestCase

from app.util.crypto import generate_new_key, create_public_key_file
from app.util.result import Result
from test.test_auth import register_user_happy_path
from test.base import BaseTestCase

TEST_FOLDER = Path(__file__).resolve().parent
PUBLIC_KEY_FILE = TEST_FOLDER / "public.pem"


class TestCrypto(BaseTestCase):
    def test_jwt_algorithm_hs256(self):
        with self.client:
            # verify auth token still created when rsa parameter missing
            self.app.config["JWT_KEY_N"] = None
            jwt_auth = register_user_happy_path(self)
            self.assertIsNotNone(jwt_auth)
            auth_status_response = self.client.get(
                "api/v1/auth/status", headers=dict(Authorization=f"Bearer {jwt_auth}")
            )
            auth_status_data = auth_status_response.get_json()
            self.assertEqual(auth_status_data["email"], "new_user@email.com")
            self.assertFalse(auth_status_data["admin"])
            self.assertEqual(auth_status_response.status_code, HTTPStatus.OK)

    def test_generate_rsa_key(self):
        # redirect stdout to suppress rsa parameters being output during test
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        # rsa parameters are printed to stdout when method below is called
        result = generate_new_key()
        self.assertTrue(result.success)
        key = result.value
        self.assertIsNotNone(key)
        # reset stdout to stop output from being suppressed
        sys.stdout = sys.__stdout__

    def test_create_public_key_file(self):
        # verify public key created when file does not exist
        self.assertFalse(PUBLIC_KEY_FILE.exists())
        result = create_public_key_file(static_folder=TEST_FOLDER)
        self.assertTrue(result.success)
        self.assertTrue(PUBLIC_KEY_FILE.exists())
        # verify public key created when file alraedy exists
        result = create_public_key_file(static_folder=TEST_FOLDER)
        self.assertTrue(result.success)
        self.assertTrue(PUBLIC_KEY_FILE.exists())
        # remove public key file created by test case
        PUBLIC_KEY_FILE.unlink()
        self.assertFalse(PUBLIC_KEY_FILE.exists())
        # verify error when rsa parameter missing
        self.app.config["JWT_KEY_N"] = None
        result = create_public_key_file(static_folder=TEST_FOLDER)
        self.assertFalse(result.success)
        self.assertFalse(PUBLIC_KEY_FILE.exists())
        self.assertEqual(
            result.error,
            "One or more required key values not found, unable to construct RSA encryption key.",
        )


if __name__ == "__main__":
    unittest.main()
