from flask_marshmallow import Marshmallow
from models import *

ma = Marshmallow()

class VTuberSchema(ma.Schema):
    hashtags = ma.Nested('HashTagSchema')
    avatar = ma.Nested('AvatarSchema')
    aliases = ma.Nested('AliasSchema', many=True)
    social = ma.Nested('SocialSchema', many=True)
    songs = ma.Nested('SongsSchema', many=True)

    class Meta:
        model = VTuber
        fields = (
            "id","fullname", "kanji", "gender", "age", "units",
            "debut", "fanname", "zodiac", "birthday", "height",
            "youtube", "illust"
        )

class HashTagSchema(ma.Schema):
    class Meta:
        model = HashTags
        fields = ("stream_tag", "fanart_tag")

class AvatarSchema(ma.Schema):
    class Meta:
        model = Avatar
        fields = ("file", "source", "creator", "app")

class AliasSchema(ma.Schema):
    class Meta:
        model = Aliases
        fields = ('id', 'alias')

class SongsSchema(ma.Schema):
    class Meta:
        model = Songs
        fields = (
            'id', 'name', 'album', 'releasedate',
            'compositor', 'lyrics', 'albumpt'
        )

class SocialSchema(ma.Schema):
    class Meta:
        model = Social
        fields = ("id", "socialapp", "socialurl")

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