from flask import Blueprint, request, jsonify
from .models import Image, images_schema, User, image_schema
from sqlalchemy import desc
from . import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_cors import CORS

images_blueprint = Blueprint("images", __name__)

CORS(images_blueprint)


@images_blueprint.get("<index>")
def current_image(index):
    image = Image.query.filter_by(id=index).first()
    result = image_schema.dump(image)

    return jsonify({"result": result}), 200


@images_blueprint.post("add")
@jwt_required()
def add_image():
    image = request.json['image']
    current_user = get_jwt_identity()

    if image:
        url = image
    else:
        return jsonify({"message": "No image selected!", "success": False}), 400

    user = User.query.filter_by(id=current_user).first()
    new_image = Image(url, user.id)
    db.session.add(new_image)
    db.session.commit()

    return jsonify({"message": "Image Added!", "success": True}), 201


@images_blueprint.delete("delete/<index>")
@jwt_required()
def delete_image(index):
    image = Image.query.filter_by(id=index).first()

    db.session.delete(image)
    db.session.commit()

    return jsonify({"message": "Image Deleted!", "success": True}), 202


@images_blueprint.get("all")
@jwt_required()
def images():
    current_user = get_jwt_identity()
    page = request.headers.get('page', 1, type=int)
    per_page = 6
    all_images = Image.query.order_by(desc(Image.date)).filter_by(user_id=current_user).\
        paginate(page=page, per_page=per_page)
    result = images_schema.dump(all_images.items)

    meta = {
        "page": all_images.page,
        "pages": all_images.pages,
        "total_count": all_images.total,
        "prev_page": all_images.prev_num,
        "next_page": all_images.next_num,
        "has_prev": all_images.has_prev,
        "has_next": all_images.has_next
    }

    return jsonify({"result": result, "meta": meta}), 200
