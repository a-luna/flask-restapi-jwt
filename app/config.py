import os
from pathlib import Path

from dotenv import load_dotenv


APP_FOLDER = Path(__file__).resolve().parent
APP_ROOT = APP_FOLDER.parent
DOTENV_PATH = APP_ROOT / '.env'
DB_URL_SQLITE = 'sqlite:///' + str(APP_FOLDER / 'flask_restapi_jwt_prod.db')
DB_URL_DEV = 'sqlite:///' + str(APP_FOLDER / 'flask_restapi_jwt_dev.db')
DB_URL_TEST = 'sqlite:///' + str(APP_FOLDER / 'flask_restapi_jwt_test.db')

class Config:
    """Base configuration."""

    if Path(DOTENV_PATH).is_file():
        load_dotenv(DOTENV_PATH)
    SECRET_KEY = os.getenv('SECRET_KEY', 'open_sesame')
    DEBUG = True
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    AUTH_TOKEN_AGE_HOURS = 0
    AUTH_TOKEN_AGE_MINUTES = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False

class DevelopmentConfig(Config):
    """Development configuration."""

    BCRYPT_LOG_ROUNDS = 4
    AUTH_TOKEN_AGE_MINUTES = 15
    SQLALCHEMY_DATABASE_URI = DB_URL_DEV

class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = DB_URL_TEST

class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    AUTH_TOKEN_AGE_HOURS = 1
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DB_URL_SQLITE)
    PRESERVE_CONTEXT_ON_EXCEPTION = True


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY