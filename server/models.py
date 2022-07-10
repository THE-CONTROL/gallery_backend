from . import db
from flask_marshmallow import Marshmallow
from datetime import datetime

ma = Marshmallow()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), nullable=False, unique=True)
    email = db.Column(db.String(1000), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)
    picture = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship("Image", backref="user")
    songs = db.relationship("Song", backref="user")
    videos = db.relationship("Video", backref="user")

    def __init__(self, username, email, password, picture):
        self.username = username
        self.email = email
        self.password = password
        self.picture = picture


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password', 'picture', 'date')


user_schema = UserSchema()


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, image, user_id):
        self.image = image
        self.user_id = user_id


class ImageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'image', 'user_id', 'date')


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    song_name = db.Column(db.String(1000))

    def __init__(self, song, user_id, song_name):
        self.song = song
        self.user_id = user_id
        self.song_name = song_name


class SongSchema(ma.Schema):
    class Meta:
        fields = ('id', 'song', 'user_id', 'song_name', 'date')


song_schema = SongSchema()
songs_schema = SongSchema(many=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    video_name = db.Column(db.String(1000))

    def __init__(self, video, user_id, video_name):
        self.video = video
        self.user_id = user_id
        self.video_name = video_name


class VideoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'video', 'user_id', 'video_name', 'date')


video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)
