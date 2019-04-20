"""URL route definitions for secure authorization tool."""
import json
from flask import render_template, flash, redirect, url_for

from app.routes import routes_bp
from app.util.crypto import get_public_key_hex


@routes_bp.route("/secure_auth", methods=["GET", "POST"])
def secure_auth():
    result = get_public_key_hex()
    if result.failure:
        flash(result.error)
        return redirect(url_for("routes.secure_auth"))
    public_key = result.value

    return render_template(
        "auth.html",
        title="Secure Authorization Tool",
        public_key=public_key,
    )
