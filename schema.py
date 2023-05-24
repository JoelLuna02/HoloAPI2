from flask_marshmallow import Marshmallow
from models import VTuber

ma = Marshmallow()

class VTuberSchema(ma.Schema):
    class Meta:
        model = VTuber
        fields = (
            "id", "fullname", "kanji", "gender", "age", "units",
            "debut", "fanname", "zodiac", "birthday", "height",
            "youtube"
        )

