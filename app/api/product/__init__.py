from flask_restplus import Namespace

product_ns = Namespace(name="product", validate=True)

from app.api.product import endpoints
