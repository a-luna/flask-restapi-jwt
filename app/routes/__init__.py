from flask import Blueprint

routes_bp = Blueprint('routes', __name__, url_prefix='/')

from app.routes import redirects