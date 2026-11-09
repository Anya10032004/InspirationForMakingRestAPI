from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Store a hash, never plain text.
    role = db.Column(db.String(20), nullable=False)

    merchant = db.relationship("Merchant", back_populates="user", uselist=False)
    claims = db.relationship("Claim", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


class Merchant(db.Model):
    __tablename__ = "merchants"

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(50))

    user = db.relationship("User", back_populates="merchant")
    products = db.relationship("Product", back_populates="merchant", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "store_name": self.store_name,
            "description": self.description,
            "user_id": self.user_id,
            "address": self.address,
            "phone": self.phone,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey("merchants.id"), nullable=False)

    merchant = db.relationship("Merchant", back_populates="products")
    claims = db.relationship("Claim", back_populates="product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "merchant_id": self.merchant_id,
        }


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product", back_populates="claims")
    user = db.relationship("User", back_populates="claims")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
        }
