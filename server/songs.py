from flask import Blueprint, request, jsonify
from .models import Song, songs_schema, User, song_schema
from sqlalchemy import desc
from . import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import CORS

songs_blueprint = Blueprint("songs", __name__)

CORS(songs_blueprint)


@songs_blueprint.get("<index>")
@jwt_required()
def current_song(index):
    song = Song.query.filter_by(id=index).first()
    result = song_schema.dump(song)

    return jsonify({"result": result}), 200


@songs_blueprint.post("add")
@jwt_required()
def add_song():
    song = request.json['song']
    song_name = request.json['song_name']
    current_user = get_jwt_identity()

    if Song.query.filter_by(song_name=song_name).first() is not None:
        return jsonify({"message": "Song already exists!", "success": False}), 409

    if song:
        url = song
    else:
        return jsonify({"message": "No song selected!", "success": False}), 400

    user = User.query.filter_by(id=current_user).first()
    new_song = Song(url, user.id, song_name)
    db.session.add(new_song)
    db.session.commit()

    return jsonify({"message": "Song Added!", "success": True}), 201


@songs_blueprint.delete("delete/<index>")
@jwt_required()
def delete_song(index):
    song = Song.query.filter_by(id=index).first()

    db.session.delete(song)
    db.session.commit()

    return jsonify({"message": "Song Deleted!", "success": True}), 202


@songs_blueprint.get("all")
@jwt_required()
def songs():
    current_user = get_jwt_identity()
    page = request.headers.get('page', 1, type=int)
    per_page = 6
    all_songs = Song.query.order_by(desc(Song.date)).filter_by(user_id=current_user).\
        paginate(page=page, per_page=per_page)
    result = songs_schema.dump(all_songs.items)

    meta = {
        "page": all_songs.page,
        "pages": all_songs.pages,
        "total_count": all_songs.total,
        "prev_page": all_songs.prev_num,
        "next_page": all_songs.next_num,
        "has_prev": all_songs.has_prev,
        "has_next": all_songs.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200
