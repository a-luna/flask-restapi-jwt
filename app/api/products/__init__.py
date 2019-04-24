from flask_restplus import Namespace

product_ns = Namespace(name="products", validate=True)

from app.api.products import endpoints
