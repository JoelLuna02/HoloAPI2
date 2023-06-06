import os
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SHOW_SQLALCHEMY_LOG_MESSAGES = False
JWT_SECRET_KEY = os.getenv("JWT_SECRET")
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = os.getenv("SECRET_KEY")

APISPEC_SPEC = APISpec(
    title='HoloAPI Documentation',
    version='1.0.0',
    openapi_version='3.0.3',
    plugins=[MarshmallowPlugin()]
)
APISPEC_SWAGGER_URL = os.getenv("APISPEC_SWAGGER")

ERROR_404_HELP = False
