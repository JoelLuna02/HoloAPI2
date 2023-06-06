from flask_apispec.extension import FlaskApiSpec
from flask import Flask, request, render_template, json
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

import random

apli = Flask(__name__)          # Flask App
apli.config.from_object(conf)   # Flask Config
db.init_app(apli)               # SQLAlchemy init
ma.init_app(apli)               # Marshmallow init
vtapi.init_app(apli)
userapi.init_app(apli)
fileapi.init_app(apli)

mi = Migrate(apli, db)          # Migrate init
cors = CORS(apli)               # CORS method init
jwt = JWTManager(apli)          # JSON Web Token method init
docs = FlaskApiSpec(apli)       # Flask APISPEC Init for documentation
jwtProviders(jwt)               # Define JWT Exceptions
flask_exceptions(apli)          # Define Flask Exceptions

docs.register(ListVTubers)
docs.register(ListSongs)
docs.register(GetVTuber)
docs.register(RandomVTuber)
docs.register(GetSong)
docs.register(FindVTuber)

# Flask common routes and routines

@apli.route("/v1")
def ahelp():
    accept = request.headers.get('Accept')
    if accept and 'text/html' in accept:
        return '<h1>Helper</h1>'
    return apih, 200

@apli.route("/docs")
def docs():
    return render_template("docs.html")

@apli.route("/")
def index():
    totalvt = 0
    totalali = 0
    totalsocial = 0
    vtubers = VTuber.query.all()
    vtdata = vtuber_schema.dump(vtubers, many=True)
    for vt in vtdata:
        for aliase in vt["aliases"]:
            totalali += 1
        for socialn in vt["social"]:
            totalsocial += 1
        totalvt += 1
    rnddata = []    # List to store six vtubers randomly
    for i in range(0, 6):
        rnddata.append(vtdata.pop(vtdata.index(random.choice(vtdata))))
    return render_template("index.html", vtuber=rnddata, total_vtubers=totalvt, total_aliases=totalali, total_social=totalsocial)

if __name__ == '__main__':
    apli.run(debug=False)
