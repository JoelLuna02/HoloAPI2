from flask_marshmallow import Marshmallow
from marshmallow import fields
from models import *

ma = Marshmallow()

class VTuberSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    fullname = fields.String()
    kanji = fields.String()
    gender = fields.String()
    age = fields.Integer()
    units = fields.List(fields.String())
    debut = fields.String()
    fanname = fields.String()
    zodiac = fields.String()
    birthday = fields.String()
    height = fields.Integer()
    youtube = fields.Url()
    illust = fields.String()
    hashtags = ma.Nested('HashTagSchema')
    avatar = ma.Nested('AvatarSchema')
    aliases = ma.Nested('AliasSchema', many=True)
    social = ma.Nested('SocialSchema', many=True)
    songs = ma.Nested('SongsSchema', many=True)

class HashTagSchema(ma.Schema):
    stream_tag = fields.String()
    fanart_tag = fields.String()

class AvatarSchema(ma.Schema):
    file = fields.Url()
    source = fields.Url()
    creator = fields.String()
    app = fields.String()

class SocialSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    socialapp = fields.String()
    socialurl = fields.Url()

class AliasSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    alias = fields.String()

class SongsSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    album = fields.String()
    releasedate = fields.String()
    compositor = fields.String()
    lyrics = fields.String()
    albumpt = fields.Url()
    



class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'is_admin'
        )


class FileSchema(ma.Schema):
    class Meta:
        model = File
        fields = ("id", "filename", "integrity")
