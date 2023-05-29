from flask_apispec.extension import FlaskApiSpec
from flask_bootstrap import Bootstrap5
from flask import Flask, request, render_template
from apispec import APISpec
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import config.default as conf
from apihelp import apih
from models import *
from schema import *

from jwtprovider import jwtProviders
from vtubers import *
from users import *
from filestorage import *
from exceptions import flask_exceptions

apli = Flask(__name__)          # Flask App
apli.config.from_object(conf)   # Flask Config
db.init_app(apli)               # SQLAlchemy init
ma.init_app(apli)               # Marshmallow init
bootstrap = Bootstrap5(apli)
vtapi.init_app(apli)
userapi.init_app(apli)
fileapi.init_app(apli)

mi = Migrate(apli, db)          # Migrate init
cors = CORS(apli)               # CORS method init
jwt = JWTManager(apli)          # JSON Web Token method init
docs = FlaskApiSpec(apli)
jwtProviders(jwt)
flask_exceptions(apli)

docs.register(ListVTubers)
docs.register(GetVTuber)
docs.register(FindVTuber)
docs.register(CreateVTuber)
docs.register(DeleteVTuber)
docs.register(UpdateVTuber)

# Flask common routes and routines

@apli.route("/v1")
def ahelp():
    accept = request.headers.get('Accept')
    if accept and 'text/html' in accept:
        return '<h1>Helper</h1>'
    return apih, 200

@apli.route("/docs")
def docs():
    return render_template("index.html")


if __name__ == '__main__':
    apli.run(debug=False)
