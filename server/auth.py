from flask import Blueprint, request, jsonify
from .models import User, Image, Song, Video, user_schema
import validators
from flask_bcrypt import Bcrypt
from . import db
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()

CORS(auth)

default = "http://res.cloudinary.com/de49puo0s/image/upload/v1656062130/q8azx8vnrpdehxjkh4bh.jpg"


@auth.post("register")
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    password1 = request.json['password1']
    picture = request.json['picture']

    if len(username) < 3:
        return jsonify({"message": "Username must be greater than two characters!", 'success': False}), 400
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message": "User already exists!", 'success': False}), 409
    if not validators.email(email):
        return jsonify({"message": "Email not valid!", 'success': False}), 400
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"message": "Email already exists!", 'success': False}), 409
    if len(password) < 6:
        return jsonify({"message": "Password must be greater than five characters!", 'success': False}), 400
    if password != password1:
        return jsonify({"message": "Passwords don't match!", 'success': False}), 400

    if picture:
        url = picture
    else:
        url = default

    password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(username, email, password, url)
    refresh = create_refresh_token(identity=user.id)
    access = create_access_token(identity=user.id)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Created!", 'success': True, "access": access,
                    "refresh": refresh}), 201


@auth.put("update")
@jwt_required()
def update():
    username = request.json['username']
    email = request.json['email']
    picture = request.json['picture']

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if len(username) < 3:
        return jsonify({"message": "Username must be greater than two characters!", 'success': False}), 400
    if User.query.filter_by(username=username).first() is not None and username != user.username:
        return jsonify({"message": "User already exists!", 'success': False}), 409
    if not validators.email(email):
        return jsonify({"message": "Email not valid!", 'success': False}), 400
    if User.query.filter_by(email=email).first() is not None and email != user.email:
        return jsonify({"message": "Email already exists!", 'success': False}), 409

    if picture:
        url = picture
    else:
        url = default

    user.username = username
    user.email = email
    user.picture = url

    db.session.commit()

    return jsonify({"message": "User Updated!", 'success': True}), 200


@auth.post("login")
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        refresh = create_refresh_token(identity=user.id)
        access = create_access_token(identity=user.id)

        return jsonify({
            'tokens': {
                'refresh': refresh,
                'access': access
            },
            'message': 'Login successful!',
            'success': True
        }), 200

    else:
        return jsonify({'message': 'Check your login details!', 'success': False}), 400


@auth.get("user")
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    result = user_schema.dump(user)

    return jsonify({"user": result})


@auth.delete("delete")
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    images = Image.query.filter_by(user_id=user_id).all()
    songs = Song.query.filter_by(user_id=user_id).all()
    videos = Video.query.filter_by(user_id=user_id).all()

    db.session.delete(user)
    if images:
        for image in images:
            db.session.delete(image)

    if songs:
        for song in songs:
            db.session.delete(song)

    if videos:
        for video in videos:
            db.session.delete(video)

    db.session.commit()

    return jsonify({"message": "User deleted!", "success": True}), 202


@auth.post("refresh")
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({"access": access}), 200
