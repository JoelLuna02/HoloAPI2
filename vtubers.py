import random
from flask import request
from werkzeug.exceptions import NotFound, Forbidden
from flask_restful import Api, Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_apispec import doc, marshal_with
from flask_apispec.views import MethodResource
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import fields
from models import Avatar, Aliases, VTuber, Songs, Social
from schema import *

vtuber_schema = VTuberSchema()
hashtags_schema = HashTagSchema()
avatar_schema = AvatarSchema()
alias_schema = AliasSchema(many=True)
social_schema = SocialSchema(many=True)
song_schema = SongsSchema(many=True)


createvtuber_help = '''
THIS RESOURCE IS PROTECTED, SO YOU CANNOT GET ACCESS TO USE.

This method creates a new VTuber and stores in the database. if already exists a vtuber by fullname, fanname, youtube url, etc., the program returns a 500 error.
'''

vtapi = Api()

class ListVTubers(Resource, MethodResource):
    @doc(description="VTuber's full list.", tags=['VTuber Resource'])
    @marshal_with(VTuberSchema(many=True), description='This method returns a vtuber full list from the database', code=200)
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

class ListSongs(Resource, MethodResource):
    @doc(description="Songs full list.", tags=['Songs Resource'])
    @marshal_with(SongsSchema(many=True), description='This method returns a full list of songs of vtubers from the database', code=200)
    def get(self):
        songs = Songs.query.all()
        response = song_schema.dump(songs, many=True)
        return response, 200

class ListAlias(Resource, MethodResource):
    @doc(description="Aliases full list.", tags=['Alias Resource'])
    @marshal_with(VTuberSchema(many=True), description='This method returns a full list of aliases of vtubers from the database', code=200)
    def get(self):
        aliases = Aliases.query.all()
        response = alias_schema.dump(aliases, many=True)
        return response, 200

class GetVTuber(Resource, MethodResource):
    @doc(description='Get a VTuber by ID.', tags=['VTuber Resource'], params={'vtid': {'description': 'The VTuber id'}})
    @marshal_with(VTuberSchema, description='This method returns a vtuber with her/his information by id. If not exists, returns a 404 error.', code=200)
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

class RandomVTuber(Resource, MethodResource):
    @doc(description="Get random VTuber", tags=['VTuber Resource'])
    @marshal_with(VTuberSchema, description='This method returns a random vtuber from the database', code=200)
    def get(self):
        vtubers = VTuber.query.all()
        vtsdict = vtuber_schema.dump(vtubers, many=True)
        vtuber = random.choice(vtsdict)
        response = vtuber_schema.dump(vtuber)
        return response, 200

class GetSong(Resource, MethodResource):
    @doc(description='Get a Song by ID.', tags=['Songs Resource'], params={'sngid': {'description': 'The Song id, required to find by id'}})
    @marshal_with(SongsSchema, description='This method returns a song information by id. If not exists, returns a 404 error.', code=200)
    def get(self, sngid:int):
        song = db.session.get(Songs, sngid)
        if song is None:
            raise NotFound("Song not found.")
        response = song_schema.dump(song, many=False)
        return response, 200

class GetAlias(Resource, MethodResource):
    def get(self, alid):
        alias = db.session.get(Aliases, alid)
        if alias is None:
            raise NotFound("Alias not found")
        response = alias_schema.dump(alias, many=False)
        return response, 200

class FindVTuber(Resource, MethodResource):
    @doc(description='Find a VTuber.', tags=['VTuber Resource'])
    @marshal_with(VTuberSchema, description='This method find and return a vtuber with her/his information, if it exists by params. Parameters available: fullname, kanji, fanname and youtube.', code=200)
    def get(self):
        params = request.args.to_dict()
        try:
            vtuber = VTuber.query.filter_by(**params).one()
            if vtuber is None:
                raise NotFound("The VTuber does not exists.")
            response = vtuber_schema.dump(vtuber)
            response['hashtags'] = hashtags_schema.dump(vtuber.hashtags)
            response['avatar'] = avatar_schema.dump(vtuber.avatar)
            response['aliases'] = alias_schema.dump(vtuber.aliases)
            response["social"] = social_schema.dump(vtuber.social)
            response['songs'] = song_schema.dump(vtuber.songs)
            return response, 200
        except NoResultFound as noresult:
                raise NotFound("The VTuber does not exists")


class CreateVTuber(Resource, MethodResource):
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
            "status": "created",
            "code": 201
        }
        response["vtuber"]["hashtags"] = hashtags_schema.dump(hashtag)
        response["vtuber"]["avatar"] = avatar_schema.dump(avatar)
        response["vtuber"]["aliases"] = alias_schema.dump(aliasdict)
        response["vtuber"]["social"] = social_schema.dump(socialdict)
        response["vtuber"]["songs"] = song_schema.dump(songsdict)
        return response, 201

class AddSong(Resource, MethodResource):
    @jwt_required()
    def post(self, vtid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        songdict = request.get_json()
        song = Songs(
            name=songdict['name'], album=songdict["album"], releasedate=songdict["releasedate"],
            compositor=songdict['compositor'], lyrics=songdict['lyrics'], albumpt=songdict['albumpt']
        )
        db.session.flush()
        song.vtid = vtuber.id
        vtuber.songs.append(song)
        db.session.add(song)
        db.session.commit()
        response = {
            "song": song_schema.dump(song, many=False),
            "message": f"Succssfully Song added to the vtuber {vtid}",
            "status": "Created",
            "code": 201
        }
        return response, 201

class AddAlias(Resource, MethodResource):
    @jwt_required()
    def post(self, vtid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        vtuber = db.session.get(VTuber, vtid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        alidict = request.get_json()
        alias = Aliases(alias=alidict["alias"])
        db.session.flush()
        alias.vt_id = vtuber.id
        vtuber.aliases.append(alias)
        db.session.add(alias)
        db.session.commit()
        response = {
            "new_alias": alias_schema.dump(alias, many=False),
            "message": f"Succssfully Alias added to the vtuber {vtid}",
            "status": "Created",
            "code": 201
        }
        return response, 201

class DeleteVTuber(Resource, MethodResource):
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

class DeleteSong(Resource, MethodResource):
    @jwt_required()
    def delete(self, sngid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        song = db.session.get(Songs, sngid)
        if song is None:
            raise NotFound("Song not found.")
        db.session.delete(song)
        db.session.commit()
        return {}, 204

class DeleteAlias(Resource, MethodResource):
    @jwt_required()
    def delete(self, alid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        alias = db.session.get(Aliases, alid)
        if alias is None:
            raise NotFound("Alias not found.")
        db.session.delete(alias)
        db.session.commit()
        return {}, 204

class UpdateVTuber(Resource, MethodResource):
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

class UpdateSong(Resource, MethodResource):
    @jwt_required()
    def patch(self, vtid:int, sngid:int):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        vtuber = db.session.get(VTuber, vtid)
        song = db.session.get(Songs, sngid)
        songdict = request.get_json()
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        elif song is None or song not in vtuber.songs:
            raise NotFound("Song not found or does not appears in the vtuber data.")
        
        if songdict:
            song.name = songdict.get('name', song.name)
            song.album = songdict.get('album', song.album)
            song.releasedate = songdict.get('releasedate', song.releasedate)
            song.compositor = songdict.get('compositor', song.compositor)
            song.lyrics = songdict.get('lyrics', song.lyrics)
            song.albumpt = songdict.get('albumpt', song.albumpt)
            db.session.commit()     # Save the changes
            response = {
                "song": song_schema.dump(song, many=False),
                "message": f"Succssfully Song of id {sngid} updated to the vtuber {vtid}",
                "status": "OK",
                "code": 200
            }
            return response, 200
        else:
            response = {
                "song": song_schema.dump(song, many=False),
                "message": f"Nothing to changes",
                "status": "OK",
                "code": 200
            }
            return response, 200

class UpdateAlias(Resource, MethodResource):
    @jwt_required()
    def patch(self, vtid:int, alid:int):
        userid = get_jwt_identity()
        alidict = request.get_json()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        vtuber = db.session.get(VTuber, vtid)
        alias = db.session.get(Aliases, alid)
        if vtuber is None:
            raise NotFound("The VTuber does not exists.")
        elif alias is None or alias not in vtuber.aliases:
            raise NotFound("Alias not found or does not appears in the vtuber data.")
        if alidict:
            alias.alias = alidict.get("alias", alias.alias)
            db.session.commit()
            response = {
                "alias": alias_schema.dump(alias, many=False),
                "message": f"Succssfully Alias of id {alid} updated to the vtuber {vtid}",
                "code": 200,
                "status": "OK"
            }
            return response, 200
        else:
            response = {
                "alias": alias_schema.dump(alias, many=False),
                "message": f"Nothing to changes",
                "code": 200,
                "status": "OK"
            }
            return response, 200

vtapi.add_resource(ListVTubers, "/v1/vtuber")
vtapi.add_resource(ListSongs, '/v1/songs')
vtapi.add_resource(ListAlias, '/v1/aliases')

vtapi.add_resource(GetVTuber, "/v1/vtuber/<int:vtid>")
vtapi.add_resource(GetSong, "/v1/songs/<int:sngid>")
vtapi.add_resource(GetAlias, '/v1/aliases/<int:alid>')
vtapi.add_resource(FindVTuber, '/v1/vtuber/find')
vtapi.add_resource(RandomVTuber, '/v1/vtuber/random')

vtapi.add_resource(CreateVTuber, "/v1/vtuber/create")
vtapi.add_resource(AddSong, '/v1/songs/add/<int:vtid>')
vtapi.add_resource(AddAlias, '/v1/aliases/add/<int:vtid>')
vtapi.add_resource(DeleteVTuber, "/v1/vtuber/delete/<int:vtid>")
vtapi.add_resource(DeleteSong, "/v1/songs/delete/<int:sngid>")
vtapi.add_resource(DeleteAlias, "/v1/aliases/delete/<int:alid>")
vtapi.add_resource(UpdateVTuber, "/v1/vtuber/update/<int:vtid>")
vtapi.add_resource(UpdateSong, "/v1/songs/update/<int:vtid>/<int:sngid>")
vtapi.add_resource(UpdateAlias, "/v1/aliases/update/<int:vtid>/<int:alid>")
