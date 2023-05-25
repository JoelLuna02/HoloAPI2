from datetime import datetime
from flask import Flask, abort, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException, NotFound
from flask_cors import CORS
import config.default as conf
from models import *
from schema import *

apli = Flask(__name__)          # Flask App
apli.config.from_object(conf)   # Flask Config
db.init_app(apli)               # SQLAlchemy init
ma.init_app(apli)               # Marshmallow init
api = Api(apli)                 # Restful init
mi = Migrate(apli, db)          # Migrate init
cors = CORS(apli)

vtuber_schema = VTuberSchema()
hashtags_schema = HashTagSchema()
avatar_schema = AvatarSchema()
parser = reqparse.RequestParser()
parser.add_argument('fullname', type=str, help="VTuber's fullname")

# API REST Routes

class ListVTubers(Resource):
    def get(self):
        vtubers = VTuber.query.all()
        response = vtuber_schema.dump(vtubers, many=True)
        for vt, rep in zip(vtubers, response):
            rep['hashtags'] = hashtags_schema.dump(vt.hashtags)
            rep['avatar'] = avatar_schema.dump(vt.avatar)
        return response, 200

class GetVTuber(Resource):
    def get(self, vtid:int):
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        response = vtuber_schema.dump(vtuber)
        response['hashtags'] = hashtags_schema.dump(vtuber.hashtags)
        response['avatar'] = avatar_schema.dump(vtuber.avatar)
        return response, 200

class CreateVTuber(Resource):
    def post(self):
        vtdict = request.get_json()
        vtuber = VTuber(
            fullname=vtdict["fullname"], kanji=vtdict["kanji"], gender=vtdict["gender"],
            age=int(vtdict["age"]), units=vtdict["units"], debut=vtdict["debut"],
            fanname=vtdict["fanname"], zodiac=vtdict["zodiac"], birthday=vtdict["birthday"],
            height=int(vtdict["height"]), youtube=vtdict["youtube"], illust=vtdict["illust"]
        )
        db.session.add(vtuber)
        db.session.flush()

        hashtag = HashTags(
            stream_tag=vtdict["hashtags"]["stream_tag"],
            fanart_tag=vtdict["hashtags"]["fanart_tag"],
        )
        avatar = Avatar(
            file=vtdict["avatar"]["file"], source=vtdict["avatar"]["source"], 
            creator=vtdict["avatar"]["creator"], app=vtdict["avatar"]["app"]
        )
        hashtag.vtuber_id = vtuber.id
        avatar.vtuber_id = vtuber.id
        db.session.add(hashtag)
        db.session.add(avatar)
        db.session.commit()

        response = {
            "vtuber": vtuber_schema.dump(vtuber),
            "message": "VTuber created sucessfully",
            "status": "201 created"
        }
        response["vtuber"]["hashtags"] = hashtags_schema.dump(hashtag)
        response["vtuber"]["avatar"] = avatar_schema.dump(avatar)
        return response, 201

class DeleteVTuber(Resource):
    def delete(self, vtid:int):
        vtuber = vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        if vtuber.hashtags and vtuber.avatar:
            db.session.delete(vtuber.hashtags)
            db.session.delete(vtuber.avatar)
        db.session.delete(vtuber)
        db.session.commit()
        return {}, 204

class UpdateVTuber(Resource):
    def put(self, vtid:int):
        vtdict = request.get_json()
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")

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
        vtuber.illust = vtdict["illust"]

        if 'hashtags' in vtdict:
            vthash = vtdict["hashtags"]
            if vtuber.hashtags:
                vtuber.hashtags.stream_tag = vthash.get('stream_tag', vtuber.hashtags.stream_tag)
                vtuber.hashtags.fanart_tag = vthash.get('fanart_tag', vtuber.hashtags.fanart_tag)
            else:
                newhash = HashTags(stream_tag=vthash.get('stream_tag'), fanart_tag=vthash.get('fanart_tag'))
                vtuber.hashtags = newhash

        if 'avatar' in vtdict:
            vtavatar = vtdict["avatar"]
            if vtuber.avatar:
                vtuber.avatar.file = vtavatar.get('file', vtuber.avatar.file)
                vtuber.avatar.source = vtavatar.get('source', vtuber.avatar.source)
                vtuber.avatar.creator = vtavatar.get('creator', vtuber.avatar.creator)
                vtuber.avatar.app = vtavatar.get('app', vtuber.avatar.app)
            else:
                newav = Avatar(
                    file=vtavatar.get('file'), source=vtavatar.get('source'),
                    creator=vtavatar.get('creator'), app=vtavatar.get('app')
                )
                vtuber.avatar = newav

        db.session.commit()     # Update the data

        response = {
            "newdata": vtuber_schema.dump(vtuber),
            "message": f"Data of the vtuber {vtid} updated sucessfully",
            "status": "200 OK"
        }
        response["newdata"]["hashtags"] = hashtags_schema.dump(vtuber.hashtags)
        response["newdata"]["avatar"] = avatar_schema.dump(vtuber.avatar)
        return response, 200

api.add_resource(ListVTubers, "/v1/vtuber", endpoint='vtubers')
api.add_resource(GetVTuber, "/v1/vtuber/<int:vtid>", endpoint='get-vtuber-id')
api.add_resource(CreateVTuber, "/v1/vtuber/create", endpoint='create-vtuber')
api.add_resource(DeleteVTuber, "/v1/vtuber/delete/<int:vtid>", endpoint='delete-vtuber')
api.add_resource(UpdateVTuber, "/v1/vtuber/update/<int:vtid>", endpoint='update-vtuber')

@apli.errorhandler(HTTPException)
def error500(e):
    timestamp = datetime.now().timestamp()
    data = {
        "timestamp": timestamp,
        "status": int(e.code),
        "error": str(e.name),
        "trace": str(e.with_traceback),
        "message": str(e.description)
    }
    return jsonify(data), int(e.code)

@apli.route('/')
def index():
    return "hola mundo!"


if __name__ == '__main__':
    apli.run(debug=False)
