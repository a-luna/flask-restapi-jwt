"""Configuration classes for dev, test and production environments."""
import os
from pathlib import Path

from dotenv import load_dotenv


APP_FOLDER = Path(__file__).resolve().parent
APP_ROOT = APP_FOLDER.parent
DOTENV_PATH = APP_ROOT / ".env"
SQLITE_DEV = "sqlite:///" + str(APP_FOLDER / "flask_restapi_jwt_dev.db")
SQLITE_TEST = "sqlite:///" + str(APP_FOLDER / "flask_restapi_jwt_test.db")
SQLITE_PROD = "sqlite:///" + str(APP_FOLDER / "flask_restapi_jwt_prod.db")


class Config:
    """Base configuration."""

    if Path(DOTENV_PATH).is_file():
        load_dotenv(DOTENV_PATH)
    SECRET_KEY = os.getenv("SECRET_KEY", "open-sesame")
    JWT_KEY_N = os.getenv("JWT_KEY_N")
    JWT_KEY_E = os.getenv("JWT_KEY_E")
    JWT_KEY_D = os.getenv("JWT_KEY_D")
    JWT_KEY_P = os.getenv("JWT_KEY_P")
    JWT_KEY_Q = os.getenv("JWT_KEY_Q")
    JWT_KEY_U = os.getenv("JWT_KEY_U")
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    AUTH_TOKEN_AGE_HOURS = 0
    AUTH_TOKEN_AGE_MINUTES = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTPLUS_MASK_SWAGGER = False


class TestingConfig(Config):
    """Testing configuration."""

    ENV = "test"
    SQLALCHEMY_DATABASE_URI = SQLITE_TEST


class DevelopmentConfig(Config):
    """Development configuration."""

    ENV = "development"
    TESTING = False
    AUTH_TOKEN_AGE_MINUTES = 15
    SQLALCHEMY_DATABASE_URI = SQLITE_DEV


class ProductionConfig(Config):
    """Production configuration."""

    ENV = "production"
    DEBUG = False
    TESTING = False
    AUTH_TOKEN_AGE_HOURS = 1
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", SQLITE_PROD)
    PRESERVE_CONTEXT_ON_EXCEPTION = True


CONFIG_DICT = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)
