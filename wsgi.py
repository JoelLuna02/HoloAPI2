from datetime import datetime
from flask import Flask, abort, request, json, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_cors import CORS
import config.default as conf
from models import db, VTuber
from schema import ma, VTuberSchema

apli = Flask(__name__)          # Flask App
apli.config.from_object(conf)   # Flask Config
db.init_app(apli)               # SQLAlchemy init
ma.init_app(apli)               # Marshmallow init
api = Api(apli)                 # Restful init
mi = Migrate(apli, db)          # Migrate init
cors = CORS(apli)

# API Rest routes

vtuber_schema = VTuberSchema()

class ListVTubers(Resource):
    def get(self):
        vtuber = VTuber.query.all()
        response = vtuber_schema.dump(vtuber, many=True)
        return response, 200

class GetVTuber(Resource):
    def get(self, vtid:int):
        vtuber = VTuber.query.get(vtid)
        if vtuber is None:
            abort(404, "The VTuber does not exists.")
        response = vtuber_schema.dump(vtuber)
        return response, 200

class CreateVTuber(Resource):
    def post(self):
        data = request.get_json()
        vtdict = vtuber_schema.load(data)
        vtuber = VTuber(
            fullname=vtdict["fullname"], kanji=vtdict["kanji"], gender=vtdict["gender"],
            age=int(vtdict["age"]), units=vtdict["units"], debut=vtdict["debut"],
            fanname=vtdict["fanname"], zodiac=vtdict["zodiac"], birthday=vtdict["birthday"],
            height=int(vtdict["height"]), youtube=vtdict["youtube"]
        )
        db.session.add(vtuber)
        db.session.commit()
        response = {
            "vtuber": vtuber_schema.dump(vtuber),
            "message": "VTuber created sucessfully",
            "status": "201 created"
        }
        return response, 201

class DeleteVTuber(Resource):
    def delete(self, vtid:int):
        vtuber = VTuber.query.get(vtid)
        if vtuber is None:
            abort(404, "The VTuber does not exists.")
        db.session.delete(vtuber)
        db.session.commit()
        return {}, 204

class UpdateVTuber(Resource):
    def put(self, vtid:int):
        data = request.get_json()
        vtdict = vtuber_schema.load(data)
        vtuber = VTuber.query.get(vtid)
        if vtuber is None:
            abort(404, "The VTuber does not exists.")

        vtuber.fullname = vtdict["fullname"]
        vtuber.kanji = vtdict["kanji"]
        vtuber.gender = vtdict["gender"]
        vtuber.age = int(vtdict["age"])
        vtuber.units = vtdict["units"]
        vtuber.debut = vtdict["debut"]
        vtuber.fanname = vtdict["fanname"]
        vtuber.zodiac = vtdict["zodiac"]
        vtuber.birthday = vtdict["birthday"]
        vtuber.height = int(vtdict["height"])
        vtuber.youtube = vtdict["youtube"]

        db.session.commit()     # Update the data

        response = {
            "newdata": vtuber_schema.dump(vtuber),
            "message": f"Data of the vtuber {vtid} updated sucessfully",
            "status": "200 OK"
        }
        return response, 200

api.add_resource(ListVTubers, "/v1/vtuber", endpoint='vtubers')
api.add_resource(GetVTuber, "/v1/vtuber/<int:vtid>", endpoint='get-vtuber-id')
api.add_resource(CreateVTuber, "/v1/vtuber/create", endpoint='create-vtuber')
api.add_resource(DeleteVTuber, "/v1/vtuber/delete/<int:vtid>", endpoint='delete-vtuber')
api.add_resource(UpdateVTuber, "/v1/vtuber/update/<int:vtid>", endpoint='update-vtuber')

@apli.errorhandler(Exception)
def error500(e):
    timestamp = datetime.now().timestamp()
    data = {
        "timestamp": timestamp,
        "message": "500 internal server error",
        "description": str(e)
    }
    return jsonify(data), 500

@apli.route('/')
def index():
    return "hola mundo!"
