from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Merchant, Product
from app.routes.helpers import json_body, role_required

merchants_bp = Blueprint("merchants", __name__)


@merchants_bp.post("/merchants")
@jwt_required()
@role_required("merchant")
def create_merchant():
    data = json_body()
    store_name = data.get("store_name")

    if not store_name:
        return jsonify({"message": "Store name is required", "status": 400}), 400

    user_id = int(get_jwt_identity())

    if Merchant.query.filter_by(store_name=store_name).first():
        return jsonify({"message": "That store name is already taken", "status": 409}), 409

    if Merchant.query.filter_by(user_id=user_id).first():
        return jsonify({"message": "You already have a store", "status": 409}), 409

    merchant = Merchant(
        store_name=store_name,
        description=data.get("description"),
        user_id=user_id,
        address=data.get("address"),
        phone=data.get("phone"),
    )
    db.session.add(merchant)
    db.session.commit()

    return jsonify({
        "message": "Merchant profile created",
        "status": 201,
        "data": merchant.to_dict(),
    }), 201


@merchants_bp.get("/merchant/me")
@jwt_required()
@role_required("merchant")
def get_my_merchant():
    merchant = Merchant.query.filter_by(user_id=int(get_jwt_identity())).first()
    if not merchant:
        return jsonify({"message": "Merchant profile not found", "status": 404}), 404

    return jsonify({"message": "Merchant found", "status": 200, "data": merchant.to_dict()}), 200


@merchants_bp.put("/merchant/me")
@jwt_required()
@role_required("merchant")
def update_my_merchant():
    merchant = Merchant.query.filter_by(user_id=int(get_jwt_identity())).first()
    if not merchant:
        return jsonify({"message": "Merchant profile not found", "status": 404}), 404

    data = json_body()
    allowed_fields = {
        "store_name": "store_name",
        "description": "description",
        "address": "address",
        "phone": "phone",
    }

    for request_field, model_field in allowed_fields.items():
        if request_field in data:
            setattr(merchant, model_field, data[request_field])

    db.session.commit()
    return jsonify({"message": "Merchant updated", "status": 200, "data": merchant.to_dict()}), 200


@merchants_bp.get("/merchants")
@jwt_required()
@role_required("merchant")
def list_merchants():
    merchants = Merchant.query.order_by(Merchant.id.desc()).all()
    return jsonify({
        "message": "Merchant list",
        "status": 200,
        "data": [merchant.to_dict() for merchant in merchants],
    }), 200


@merchants_bp.get("/merchants/<int:merchant_id>")
@jwt_required()
def get_merchant_detail(merchant_id):
    merchant = db.session.get(Merchant, merchant_id)
    if not merchant:
        return jsonify({"message": "Merchant not found", "status": 404}), 404

    products = Product.query.filter_by(merchant_id=merchant_id).all()
    return jsonify({
        "message": "Merchant found",
        "status": 200,
        "data": {
            "merchant": merchant.to_dict(),
            "products": [product.to_dict() for product in products],
        },
    }), 200
