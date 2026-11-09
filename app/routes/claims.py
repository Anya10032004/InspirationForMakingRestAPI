from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Claim, Product
from app.routes.helpers import json_body, role_required

claims_bp = Blueprint("claims", __name__)


@claims_bp.post("/claims")
@jwt_required()
@role_required("user")
def create_claim():
    data = json_body()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"message": "product_id and quantity must be integers", "status": 400}), 400

    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero", "status": 400}), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Product not found", "status": 404}), 404

    if quantity > product.stock:
        return jsonify({
            "message": f"Not enough stock. Only {product.stock} remaining",
            "status": 409,
        }), 409

    # Update stock and create the claim in one transaction.
    product.stock -= quantity
    claim = Claim(
        product_id=product.id,
        user_id=int(get_jwt_identity()),
        quantity=quantity,
    )
    db.session.add(claim)
    db.session.commit()

    return jsonify({"message": "Claim created", "status": 201, "data": claim.to_dict()}), 201


@claims_bp.get("/claims")
@jwt_required()
@role_required("user")
def list_my_claims():
    user_id = int(get_jwt_identity())
    claims = Claim.query.filter_by(user_id=user_id).order_by(Claim.id.desc()).all()

    return jsonify({
        "message": "Your claims",
        "status": 200,
        "data": [claim.to_dict() for claim in claims],
    }), 200
