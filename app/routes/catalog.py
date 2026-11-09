from flask import Blueprint, jsonify, request

from app.models import Merchant, Product

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.get("/catalog")
def get_catalog():
    """Public catalog. Optional query parameters: search, merchant_id, page, per_page."""
    query = (
        Product.query
        .join(Merchant, Product.merchant_id == Merchant.id)
        .filter(Product.stock > 0)
    )

    search = request.args.get("search", type=str)
    merchant_id = request.args.get("merchant_id", type=int)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if search:
        query = query.filter(Product.product_name.ilike(f"%{search}%"))
    if merchant_id is not None:
        query = query.filter(Product.merchant_id == merchant_id)

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({
            "message": "page must be at least 1; per_page must be between 1 and 100",
            "status": 400,
        }), 400

    pagination = query.order_by(Product.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    data = []
    for product in pagination.items:
        data.append({
            "product_id": product.id,
            "product_name": product.product_name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "merchant_id": product.merchant_id,
            "store_name": product.merchant.store_name,
        })

    return jsonify({
        "message": "Product catalog",
        "status": 200,
        "data": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        },
    }), 200


@catalog_bp.get("/catalog/<int:product_id>")
def get_catalog_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found", "status": 404}), 404

    return jsonify({
        "message": "Product found",
        "status": 200,
        "data": {
            **product.to_dict(),
            "store_name": product.merchant.store_name,
        },
    }), 200
