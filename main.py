from io import BytesIO
import mimetypes
from flask import Flask, request, jsonify, send_file
from flask_restful import Api, Resource, reqparse
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException, NotFound, Forbidden, Unauthorized, BadRequest
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
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
cors = CORS(apli)               # CORS method init
jwt = JWTManager(apli)          # JSON Web Token method init

vtuber_schema = VTuberSchema()
hashtags_schema = HashTagSchema()
avatar_schema = AvatarSchema()
alias_schema = AliasSchema(many=True)
social_schema = SocialSchema(many=True)
song_schema = SongsSchema(many=True)
user_schema = UserSchema()
fileschema = FileSchema()

''' *** ----------------------- ***
    ***   API RESTFul Routes    ***
    *** ----------------------- ***
'''

class ListVTubers(Resource):
    def get(self):
        vtubers = VTuber.query.all()
        response = vtuber_schema.dump(vtubers, many=True)
        for vt, rep in zip(vtubers, response):
            rep['hashtags'] = hashtags_schema.dump(vt.hashtags)
            rep['avatar'] = avatar_schema.dump(vt.avatar)
            rep['aliases'] = alias_schema.dump(vt.aliases)
            rep['social'] = social_schema.dump(vt.social)
            rep['songs'] = song_schema.dump(vt.songs)
        return response, 200

class GetVTuber(Resource):
    def get(self, vtid:int):
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        response = vtuber_schema.dump(vtuber)
        response['hashtags'] = hashtags_schema.dump(vtuber.hashtags)
        response['avatar'] = avatar_schema.dump(vtuber.avatar)
        response['aliases'] = alias_schema.dump(vtuber.aliases)
        response["social"] = social_schema.dump(vtuber.social)
        response['songs'] = song_schema.dump(vtuber.songs)
        return response, 200

class CreateVTuber(Resource):
    @jwt_required()
    def post(self):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        
        vtdict = request.get_json()
        aliasdict = vtdict.pop('aliases', [])
        songsdict = vtdict.pop('songs', [])
        socialdict = vtdict.pop('social', [])
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

        for alias in aliasdict:
            al = Aliases(alias["alias"])
            al.vt_id = vtuber.id
            vtuber.aliases.append(al)
            db.session.add(al)
        for song in songsdict:
            sng = Songs(
                name=song['name'], album=song["album"], releasedate=song["releasedate"], 
                compositor=song["compositor"], lyrics=song["lyrics"], albumpt=song["albumpt"]
            )
            sng.vtid = vtuber.id
            vtuber.songs.append(sng)
            db.session.add(sng)
        for social in socialdict:
            soc = Social(socialapp=social["socialapp"], socialurl=social["socialurl"])
            soc.vtuber_id = vtuber.id
            vtuber.social.append(soc)
            db.session.add(soc)

        db.session.commit()

        response = {
            "vtuber": vtuber_schema.dump(vtuber),
            "message": "VTuber created sucessfully",
            "status": "201 created"
        }
        response["vtuber"]["hashtags"] = hashtags_schema.dump(hashtag)
        response["vtuber"]["avatar"] = avatar_schema.dump(avatar)
        response["vtuber"]["aliases"] = alias_schema.dump(aliasdict)
        response["vtuber"]["social"] = social_schema.dump(socialdict)
        response["vtuber"]["songs"] = song_schema.dump(songsdict)
        return response, 201

class DeleteVTuber(Resource):
    @jwt_required()
    def delete(self, vtid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        if vtuber.hashtags and vtuber.avatar:
            db.session.delete(vtuber.hashtags)
            db.session.delete(vtuber.avatar)
        for alias in vtuber.aliases:
            db.session.delete(alias)
        for song in vtuber.songs:
            db.session.delete(song)
        for social in vtuber.social:
            db.session.delete(social)
        db.session.delete(vtuber)
        db.session.commit()
        return {}, 204

class UpdateVTuber(Resource):
    @jwt_required()
    def put(self, vtid:int):
        vtdict = request.get_json()
        aliasdict = vtdict.pop('aliases', [])
        songsdict = vtdict.pop('songs', [])
        socialdict = vtdict.pop('social', [])
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
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

        existing_aliases = {alias.id: alias for alias in vtuber.aliases}
        existing_social = {social.id: social for social in vtuber.social}
        existing_songs = {songs.id: songs for songs in vtuber.songs}
        for alias_data in aliasdict:
            alias_id = alias_data.get("id")
            alias = existing_aliases.get(alias_id)
            if alias:
                alias.alias = alias_data.get("alias", alias.alias)
            else:
                newalias = Aliases(alias=alias_data["alias"])
                newalias.vtuber_id = vtuber.id
                db.session.add(newalias)
        for song_data in songsdict:
            song_id = song_data.get("id")
            song = existing_songs.get(song_id)
            if song:
                song.name = song_data.get("name", song.name)
                song.album = song_data.get("album", song.album)
                song.releasedate = song_data.get("releasedate", song.releasedate)
                song.compositor = song_data.get("compositor", song.compositor)
                song.lyrics = song_data.get("lyrics", song.lyrics)
                song.albumpt = song_data.get("albumpt", song.albumpt)
            else:
                newsong = Songs(
                    name=song_data["name"], album=song_data["album"], releasedate=song_data["releasedate"],
                    compositor=song_data["compositor"], lyrics=song_data["lyrics"], albumpt=song_data["albumpt"]
                )
                newsong.vtid = vtuber.id
                db.session.add(newsong)
        for social_data in socialdict:
            social_id = song_data.get("id")
            social = existing_social.get(social_id)
            if social:
                social.socialapp = social_data.get("socialapp", social.socialapp)
                social.socialurl = social_data.get("socialurl", social.socialurl)
            else:
                social = Social(socialapp=social_data["socialapp"], socialurl=social_data["socialurl"])
                social.vtuber_id = vtuber.id
                db.session.add(social)

        if aliasdict:
            for alias in vtuber.aliases:
                if alias.id not in [alias_data.get("id") for alias_data in aliasdict]:
                    db.session.delete(alias)
        if socialdict:
            for social in vtuber.social:
                if social.id not in [social_data.get("id") for social_data in socialdict]:
                    db.session.delete(social)
        if songsdict:
            for song in vtuber.songs:
                if song.id not in [song_data.get("id") for song_data in songsdict]:
                    db.session.delete(song)

        db.session.commit()     # Update the data

        response = {
            "newdata": vtuber_schema.dump(vtuber),
            "message": f"Data of the vtuber {vtid} updated sucessfully",
            "status": "200 OK"
        }
        response["newdata"]["hashtags"] = hashtags_schema.dump(vtuber.hashtags)
        response["newdata"]["avatar"] = avatar_schema.dump(vtuber.avatar)
        response["newdata"]["social"] = social_schema.dump(vtuber.social)
        response["newdata"]["aliases"] = alias_schema.dump(vtuber.aliases)
        response["newdata"]["songs"] = song_schema.dump(vtuber.songs)
        return response, 200

api.add_resource(ListVTubers, "/v1/vtuber", endpoint='vtubers')
api.add_resource(GetVTuber, "/v1/vtuber/<int:vtid>", endpoint='get-vtuber-id')
api.add_resource(CreateVTuber, "/v1/vtuber/create", endpoint='create-vtuber')
api.add_resource(DeleteVTuber, "/v1/vtuber/delete/<int:vtid>", endpoint='delete-vtuber')
api.add_resource(UpdateVTuber, "/v1/vtuber/update/<int:vtid>", endpoint='update-vtuber')

''' *** -------------------------------- ***
    ***   Register and login resources   ***
    *** -------------------------------- ***
'''

class GetUsers(Resource):
    @jwt_required()
    def get(self):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        users = User.query.all()
        response = user_schema.dump(users, many=True)
        return response, 201

class Register(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            firstname=data.get("firstname"), lastname=data.get("lastname"), birthday=data.get("birthday"),
            username=data.get("username"), email=data.get("email"), password=data.get("password")
        )
        user.is_admin = data.get('is_admin', False)
        db.session.add(user)
        db.session.commit()
        response = {
            "crated_user": user_schema.dump(user),
            "message": "Successfully registered user",
            "status": "201 Created"
        }
        return response, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.decrypt(password):
            access_token = create_access_token(identity=user.id)
            response = {
                "logged_as": user_schema.dump(user),
                "access_token": str(access_token)
            }
            return response, 200
        else:
            raise Unauthorized("Invalid access or Bad credentials, please check and try again")

api.add_resource(GetUsers, '/v1/auth/users')
api.add_resource(Register, '/v1/auth/signup')
api.add_resource(Login, '/v1/auth/login')


class ListStoredFiles(Resource):
    def get(self):
        Files = File.query.all()
        response = fileschema.dump(Files, many=True)
        return response, 200
    
class OpenFile(Resource):
    def get(self, filename:str):
        if filename is None:
            raise BadRequest("The filename is missing")
        archive = File.query.filter_by(filename=filename).first()
        if not archive:
            raise NotFound("File not found")
        mime = mimetypes.guess_type(archive.filename)
        return send_file(BytesIO(archive.filebytes), mimetype=mime[0], as_attachment=False, download_name=archive.filename)
        

class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=FileStorage, location='files', required=True)
        args = parser.parse_args()

        archive = args["file"]
        filename = secure_filename(archive.filename)
        archive_bytes = archive.read()
        if len(archive_bytes) >= 10485760:
            raise BadRequest("The file is too long to storage in the database. The maximum file size is 10 MB")
        
        newfile = File(filename=filename, filebytes=archive_bytes)
        newfile.integrity = newfile.set_integrity()
        db.session.add(newfile)
        db.session.commit()
        response = {"message": "Successfully storaged file in the database"}
        return response, 201

api.add_resource(UploadFile, '/v1/upload')
api.add_resource(ListStoredFiles, '/v1/assets/listfiles')
api.add_resource(OpenFile, '/v1/assets/<string:filename>')

# Flask common routes and routines

@apli.errorhandler(HTTPException)
def error500(e):
    response = {
        "error": e.name,
        "code": e.code,
        "message": e.description
    }
    return response, e.code

@apli.route('/')
def index():
    return "hola mundo!"

# JWT Extended errorhandlers

@jwt.unauthorized_loader
def unauthorized(err):
    response = {
        "code": 401,
        "error": "Unauthorized",
        "message": "You must be logged in to access this resource"
    }
    return jsonify(response), 401

@jwt.invalid_token_loader
def invalid_token(err):
    response = {
        "code": 401,
        "error": "Unauthorized",
        "message": "Invalid token. Please check and try again."
    }
    return jsonify(response), 401

@jwt.expired_token_loader
def expired_token(err):
    response = {
        "code": 401,
        "error": "Unauthorized",
        "message": "The token has expired. Please try again later"
    }
    return jsonify(response), 401

@jwt.needs_fresh_token_loader
def needsfresh(err):
    response = {
        "code": 401,
        "error": "Unauthorized",
        "message": "Invalid signature. Please try again later"
    }
    return jsonify(response), 401


if __name__ == '__main__':
    apli.run(debug=False)
