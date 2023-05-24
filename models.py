from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()

class VTuber(db.Model):
    __tablename__ = 'vtuber'                          # The table name
    id = db.Column(db.Integer, primary_key=True)      # id of vtuber
    fullname = db.Column(db.String(50), unique=True)  # Fullname
    kanji = db.Column(db.String(30), unique=True)     # Kanji name
    gender = db.Column(db.String(20))                 # Gender
    age = db.Column(db.Integer)                       # Age of vtuber
    units = db.Column(JSON)                           # List of units
    debut = db.Column(db.Date)                        # Date of debut
    fanname = db.Column(db.String(50), unique=True)
    zodiac = db.Column(db.String(20))
    birthday = db.Column(db.String(50))
    height = db.Column(db.Integer)
    youtube = db.Column(db.String(150), unique=True)

    # The constructor

    def __init__(self, fullname, kanji, gender, age:int, units, debut, fanname, zodiac, birthday, height:int , youtube):
        self.fullname = fullname
        self.kanji = kanji
        self.gender = gender
        self.age = age
        self.units = units
        self.debut = debut
        self.fanname = fanname
        self.zodiac = zodiac
        self.birthday = birthday
        self.height = height
        self.youtube = youtube

    def __str__(self):
        return f'{self.__fullname}'
