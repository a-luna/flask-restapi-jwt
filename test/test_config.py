"""Unit tests for app configurations."""
import os
import unittest

from flask_testing import TestCase

from app import create_app
from app.config import SQLITE_DEV, SQLITE_PROD, SQLITE_TEST


class TestDevelopmentConfig(TestCase):
    """Verify expected values for DevelopmentConfig settings."""

    def create_app(self):
        app = create_app("dev")
        return app

    def test_config_development(self):
        self.assertFalse(self.app is None)
        self.assertNotEqual(self.app.config["SECRET_KEY"], "open_sesame")
        self.assertTrue(self.app.config["DEBUG"])
        self.assertFalse(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], SQLITE_DEV)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_HOURS"], 0)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_MINUTES"], 15)


class TestTestingConfig(TestCase):
    """Verify expected values for TestingConfig settings."""

    def create_app(self):
        app = create_app("test")
        return app

    def test_config_testing(self):
        self.assertFalse(self.app is None)
        self.assertFalse(self.app.config["SECRET_KEY"] is "open_sesame")
        self.assertTrue(self.app.config["DEBUG"])
        self.assertTrue(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], SQLITE_TEST)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_HOURS"], 0)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_MINUTES"], 0)


class TestProductionConfig(TestCase):
    """Verify expected values for ProductionConfig settings."""

    def create_app(self):
        app = create_app("prod")
        return app

    def test_config_production(self):
        self.assertFalse(self.app is None)
        self.assertFalse(self.app.config["SECRET_KEY"] is "open_sesame")
        self.assertFalse(self.app.config["DEBUG"])
        self.assertFalse(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], SQLITE_PROD)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_HOURS"], 1)
        self.assertEqual(self.app.config["AUTH_TOKEN_AGE_MINUTES"], 0)


if __name__ == "__main__":
    unittest.main()
