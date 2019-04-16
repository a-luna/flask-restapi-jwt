"""URL route definitions for permanent redirects."""
from http import HTTPStatus

from flask import redirect, url_for

from app.routes import routes_bp


@routes_bp.route("/", methods=["GET"])
@routes_bp.route("/index", methods=["GET"])
def api_redirect():
    return redirect(url_for("api.doc"), HTTPStatus.FOUND)
