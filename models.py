from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()   

class VTuber(db.Model):
    __tablename__ = 'vtuber'                            # The table name
    id = db.Column(db.Integer, primary_key=True)      # id of vtuber
    fullname = db.Column(db.String(50), unique=True)  # Fullname
    kanji = db.Column(db.String(30), unique=True)     # Kanji name
    gender = db.Column(db.String(20))                 # Gender 
    age = db.Column(db.Integer)                       # Age of vtuber
    units = db.Column(JSON)                           # List of units
    debut = db.Column(db.Date)                        # Date of debut

    # The constructor

    def __init__(self, fullname, kanji, gender, age, units, debut):
        self.fullname = fullname
        self.kanji = kanji
        self.gender = gender
        self.age = age
        self.units = units
        self.debut = debut

    def __str__(self):
        return f'{self.__fullname}'
