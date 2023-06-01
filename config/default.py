from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root2022@localhost:3306/holoapi_test'
#SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://ujgasiulbxfwqzfg:VS66i6bkrTpRk8GiHizi@bl8yfpj5z23uvthrqmy6-mysql.services.clever-cloud.com:3306/bl8yfpj5z23uvthrqmy6'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SHOW_SQLALCHEMY_LOG_MESSAGES = False
JWT_SECRET_KEY = 'HoloAPI_213ijsdzsdf081#%$)(=ADSA_secret'
PROPAGATE_EXCEPTIONS = True

APISPEC_SPEC = APISpec(
    title='HoloAPI Documentation',
    version='1.0.0',
    openapi_version='3.0.3',
    plugins=[MarshmallowPlugin()]
)
APISPEC_SWAGGER_URL = '/swagger/'

ERROR_404_HELP = False
