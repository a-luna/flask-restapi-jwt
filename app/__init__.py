"""Flask app initialization via factory pattern."""
from pathlib import Path

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import CONFIG_DICT


APP_FOLDER = Path(__file__).resolve().parent

bootstrap = Bootstrap()
cors = CORS()
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app(config_name):
    app = Flask(__name__, root_path=APP_FOLDER)
    app.config.from_object(CONFIG_DICT[config_name])

    from app.api import api_bp

    app.register_blueprint(api_bp)

    from app.routes import routes_bp

    app.register_blueprint(routes_bp)

    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    return app
