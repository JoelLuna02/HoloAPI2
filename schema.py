from flask_marshmallow import Marshmallow
from models import VTuber, HashTags, Avatar

ma = Marshmallow()

class VTuberSchema(ma.Schema):
    hashtags = ma.Nested('HashTagSchema')
    avatar = ma.Nested('AvatarSchema')

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
        fields = ("htid", "stream_tag", "fanart_tag")

class AvatarSchema(ma.Schema):
    class Meta:
        model = Avatar
        fields = ("avid", "file", "source", "creator", "app")
