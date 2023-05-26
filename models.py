from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()       # SQLAlchemy dialect

''' *** ---------------------------------- *** 
    ***  VTUBER'S MODEL AND RELATIONSHIPS  ***
    *** ---------------------------------- ***
'''

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
    hashtags = db.relationship('HashTags', uselist=False, backref='vtuber', cascade='all, delete')
    avatar = db.relationship('Avatar', uselist=False, backref='vtuber', cascade='all, delete')
    illust = db.Column(db.String(50))
    aliases = db.relationship('Aliases', backref='vtuber', lazy=False, cascade='all, delete-orphan')
    social = db.relationship('Social', backref='vtuber', lazy=False, cascade='all, delete-orphan')
    songs = db.relationship('Songs', backref='vtuber', lazy=False, cascade='all, delete-orphan')

    def __init__(self, fullname, kanji, gender, age:int, units, debut, fanname, zodiac, birthday, height:int, youtube, illust, alias=[], social=[], song=[]):
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
        self.illust = illust
        self.aliases = alias
        self.social = social
        self.songs = song

    def __str__(self):
        return f'{self.__fullname}'

class HashTags(db.Model):
    __tablename__ = 'hashtags'
    htid = db.Column(db.Integer, primary_key=True)
    stream_tag = db.Column(db.String(70), unique=True)
    fanart_tag = db.Column(db.String(70), unique=True)
    vtuber_id = db.Column(db.Integer, db.ForeignKey('vtuber.id'))

    def __init__(self, stream_tag, fanart_tag):
        self.stream_tag = stream_tag
        self.fanart_tag = fanart_tag
    
    def __str__(self):
        return f"{self.stream_tag} {self.fanart_tag}"

class Avatar(db.Model):
    __tablename__ = 'avatares'
    avid = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(150), unique=True)
    source = db.Column(db.String(150), unique=True)
    creator = db.Column(db.String(50))
    app = db.Column(db.String(50))
    vtuber_id = db.Column(db.Integer, db.ForeignKey('vtuber.id'))

    def __init__(self, file, source, creator, app):
        self.file = file
        self.source = source
        self.creator = creator
        self.app = app

    def __str__(self):
        return f'{self.file}'

class Aliases(db.Model):
    __tablename__ = 'aliases'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50))
    vt_id = db.Column(db.Integer, db.ForeignKey('vtuber.id'), nullable=False)

    def __init__(self, alias):
        self.alias = alias
    
    def __str__(self):
        return f'{self.alias}'

class Social(db.Model):
    __tablename__ = 'social'
    id = db.Column(db.Integer, primary_key=True)
    socialapp = db.Column(db.String(50))
    socialurl = db.Column(db.String(150), unique=True)
    vtuber_id = db.Column(db.Integer, db.ForeignKey('vtuber.id'), nullable=False)

    def __init__(self, socialapp, socialurl):
        self.socialapp = socialapp
        self.socialurl = socialurl

class Songs(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    album = db.Column(db.String(50))
    releasedate = db.Column(db.Date)
    compositor = db.Column(db.String(40))
    lyrics = db.Column(db.String(40))
    albumpt = db.Column(db.String(170))
    vtid = db.Column(db.Integer, db.ForeignKey('vtuber.id'), nullable=False)

    def __init__(self, name, album, releasedate, compositor, lyrics, albumpt):
        self.name = name
        self.album = album
        self.releasedate = releasedate
        self.compositor = compositor
        self.lyrics = lyrics
        self.albumpt = albumpt


''' *** --------------------------- ***
    ***   USER MODEL AND METHODS    ***
    *** --------------------------- ***
'''