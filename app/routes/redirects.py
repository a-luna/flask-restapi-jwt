from flask import redirect, url_for

from app.routes import routes_bp


@routes_bp.route('/')
def home_redirect():
    return redirect(url_for('api.doc'), 302)