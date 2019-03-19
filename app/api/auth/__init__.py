from flask_restplus import Namespace

auth_ns = Namespace(name='auth', validate=True)

from app.api.auth import endpoints