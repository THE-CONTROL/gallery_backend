from flask import Blueprint, request, jsonify
from .models import Video, videos_schema, User, video_schema
from sqlalchemy import desc
from . import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import CORS

videos_blueprint = Blueprint("videos", __name__)

CORS(videos_blueprint)


@videos_blueprint.get("<index>")
@jwt_required()
def current_video(index):
    video = Video.query.filter_by(id=index).first()
    result = video_schema.dump(video)

    return jsonify({"result": result}), 200


@videos_blueprint.post("add")
@jwt_required()
def add_video():
    video = request.json['video']
    video_name = request.json['video_name']
    current_user = get_jwt_identity()

    if Video.query.filter_by(video_name=video_name).first() is not None:
        return jsonify({"message": "Video already exists!", "success": False}), 409

    if video:
        url = video
    else:
        return jsonify({"message": "No video selected"}), 400

    user = User.query.filter_by(id=current_user).first()
    new_video = Video(url, user.id, video_name)
    db.session.add(new_video)
    db.session.commit()

    return jsonify({"message": "video Added!", "success": True}), 201


@videos_blueprint.delete("delete/<index>")
@jwt_required()
def delete_video(index):
    video = Video.query.filter_by(id=index).first()

    db.session.delete(video)
    db.session.commit()

    return jsonify({"message": "video Deleted!", "success": True}), 204


@videos_blueprint.get("all")
@jwt_required()
def videos():
    current_user = get_jwt_identity()
    page = request.headers.get('page', 1, type=int)
    per_page = 6
    all_videos = Video.query.order_by(desc(Video.date)).filter_by(user_id=current_user).\
        paginate(page=page, per_page=per_page)
    result = videos_schema.dump(all_videos.items)

    meta = {
        "page": all_videos.page,
        "pages": all_videos.pages,
        "total_count": all_videos.total,
        "prev_page": all_videos.prev_num,
        "next_page": all_videos.next_num,
        "has_prev": all_videos.has_prev,
        "has_next": all_videos.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200
