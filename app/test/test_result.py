"""Unit tests for Result class."""
import unittest

from flask_testing import TestCase

from app import create_app
from app.util.result import Result

class TestResult(TestCase):

    def create_app(self):
        app = create_app('dev')
        return app

    def test_result_object(self):
        result_success = Result.Ok(42)
        self.assertTrue(result_success.success)
        self.assertFalse(result_success.failure)
        self.assertEqual(result_success.value, 42)
        self.assertIsNone(result_success.error)
        self.assertEqual(str(result_success), '[Success]')
        self.assertEqual(repr(result_success), f'Result<(success=True>')

        result_fail = Result.Fail('Something went wrong...')
        self.assertTrue(result_fail.failure)
        self.assertFalse(result_fail.success)
        self.assertIsNone(result_fail.value)
        self.assertEqual(result_fail.error, 'Something went wrong...')
        self.assertEqual(str(result_fail), '[Failure] Something went wrong...')
        self.assertEqual(repr(result_fail), f'Result<(success=False, message="Something went wrong...")>')