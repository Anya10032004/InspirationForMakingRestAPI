from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Merchant, Product
from app.routes.helpers import json_body, role_required

products_bp = Blueprint("products", __name__)


def get_current_merchant():
    return Merchant.query.filter_by(user_id=int(get_jwt_identity())).first()


def validate_product_data(data, partial=False):
    """Validate product fields and return (cleaned_data, error_message)."""
    cleaned = {}

    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, "A non-empty product name is required"
        cleaned["product_name"] = name.strip()

    if not partial or "description" in data:
        cleaned["description"] = data.get("description")

    for field in ("price", "stock"):
        if not partial or field in data:
            value = data.get(field)
            if isinstance(value, bool):
                return None, f"{field} must be a non-negative integer"
            try:
                value = int(value)
            except (TypeError, ValueError):
                return None, f"{field} must be a non-negative integer"
            if value < 0:
                return None, f"{field} cannot be negative"
            cleaned[field] = value

    return cleaned, None


@products_bp.post("/products")
@jwt_required()
@role_required("merchant")
def create_product():
    merchant = get_current_merchant()
    if not merchant:
        return jsonify({"message": "Create your merchant profile first", "status": 400}), 400

    data, error = validate_product_data(json_body())
    if error:
        return jsonify({"message": error, "status": 400}), 400

    product = Product(**data, merchant_id=merchant.id)
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product created", "status": 201, "data": product.to_dict()}), 201


@products_bp.get("/products/mine")
@jwt_required()
@role_required("merchant")
def list_my_products():
    merchant = get_current_merchant()
    if not merchant:
        return jsonify({"message": "Merchant profile not found", "status": 404}), 404

    products = Product.query.filter_by(merchant_id=merchant.id).order_by(Product.id.desc()).all()
    return jsonify({
        "message": "Your products",
        "status": 200,
        "data": [product.to_dict() for product in products],
    }), 200


@products_bp.put("/products/<int:product_id>")
@jwt_required()
@role_required("merchant")
def update_product(product_id):
    merchant = get_current_merchant()
    if not merchant:
        return jsonify({"message": "Merchant profile not found", "status": 404}), 404

    product = Product.query.filter_by(id=product_id, merchant_id=merchant.id).first()
    if not product:
        return jsonify({"message": "Product not found", "status": 404}), 404

    data = json_body()
    if not data:
        return jsonify({"message": "Provide at least one field to update", "status": 400}), 400

    cleaned, error = validate_product_data(data, partial=True)
    if error:
        return jsonify({"message": error, "status": 400}), 400

    for field, value in cleaned.items():
        setattr(product, field, value)

    db.session.commit()
    return jsonify({"message": "Product updated", "status": 200, "data": product.to_dict()}), 200


@products_bp.delete("/products/<int:product_id>")
@jwt_required()
@role_required("merchant")
def delete_product(product_id):
    merchant = get_current_merchant()
    if not merchant:
        return jsonify({"message": "Merchant profile not found", "status": 404}), 404

    product = Product.query.filter_by(id=product_id, merchant_id=merchant.id).first()
    if not product:
        return jsonify({"message": "Product not found or not owned by you", "status": 404}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted", "status": 200}), 200
