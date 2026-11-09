from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User
from app.routes.helpers import json_body

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = json_body()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = str(data.get("role", "")).lower()

    if not all([name, email, password, role]):
        return jsonify({"message": "Name, email, password, and role are required", "status": 400}), 400

    if role not in {"user", "merchant"}:
        return jsonify({"message": "Role must be either 'user' or 'merchant'", "status": 400}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists", "status": 409}), 409

    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        password=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "status": 201,
        "data": user.to_dict(),
    }), 201


@auth_bp.post("/login")
def login():
    data = json_body()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required", "status": 400}), 400

    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password", "status": 401}), 401

    # JWT claims contain identity/authorization data, never the password or its hash.
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name},
    )

    return jsonify({
        "message": "Login successful",
        "status": 200,
        "data": user.to_dict(),
        "access_token": token,
    }), 200
