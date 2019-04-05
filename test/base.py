"""Base test case class."""
from flask_testing import TestCase

from app import create_app, db


class BaseTestCase(TestCase):
    """Base test case, create app and perform db setup/teardown."""

    def create_app(self):
        app = create_app("test")
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
