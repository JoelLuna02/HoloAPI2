import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import JSON

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
    fanname = db.Column(db.String(50), unique=True)   # Fan name
    zodiac = db.Column(db.String(20))                 # Zodiac sign
    birthday = db.Column(db.String(50))               # Birthday
    height = db.Column(db.Integer)                    # Height in cm
    youtube = db.Column(db.String(150), unique=True)  # Youtube URL
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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, firstname, lastname, birthday, username, email, password, is_admin=False):
        self.firstname = firstname
        self.lastname = lastname
        self.birthday = birthday
        self.username = username
        self.email = email
        self.password = self.encrypt(password)
        self.is_admin = is_admin

    def encrypt(self, password:str):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def decrypt(self, password:str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

''' *** ------------------ ***
    ***   OTHER ENTITIES   ***
    *** ------------------ ***
'''

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), unique=True, nullable=False)
    integrity = db.Column(db.String(150), unique=True, nullable=False)
    filebytes = db.Column(db.LargeBinary(length=10485760), nullable=False)
    
    __table_args__ = (
        CheckConstraint('LENGTH(filebytes) <= 10485760', name='check_bytes_length'),
    )

    def __init__(self, filename, filebytes):
        self.filename = filename
        self.filebytes = filebytes
    
    def set_integrity(self):
        return bcrypt.hashpw(self.filebytes, bcrypt.gensalt()).decode('utf-8')
