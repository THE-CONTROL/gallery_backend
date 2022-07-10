from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_jwt_extended import JWTManager

DB_NAME = "control.db"

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'Random'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'Random'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=9000)

    db.init_app(app)

    from .auth import auth
    from .images import images_blueprint
    from .videos import videos_blueprint
    from .songs import songs_blueprint

    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(images_blueprint, url_prefix='/images/')
    app.register_blueprint(videos_blueprint, url_prefix='/videos/')
    app.register_blueprint(songs_blueprint, url_prefix='/songs/')

    from .models import User, Image, Video, Song

    create_database(app)

    jwt.init_app(app)

    return app


def create_database(app):
    if not path.exists('server/' + DB_NAME):
        db.create_all(app=app)
