from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.errors import register_error_handlers

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    """Application factory: configure and assemble the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.merchants import merchants_bp
    from app.routes.products import products_bp
    from app.routes.catalog import catalog_bp
    from app.routes.claims import claims_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(merchants_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(catalog_bp, url_prefix="/api")
    app.register_blueprint(claims_bp, url_prefix="/api")

    register_error_handlers(app)
    return app

# Traceback (most recent call last):
#   File "C:\Users\Anya\OneDrive\Documents\GitHub\multi-merchant_store\tugas_flask\run.py", line 1, in <module>
#     from app import create_app, db
#   File "C:\Users\Anya\OneDrive\Documents\GitHub\multi-merchant_store\tugas_flask\app\__init__.py", line 7, in <module>
#     from app.routes.auth import auth_bp
#   File "C:\Users\Anya\OneDrive\Documents\GitHub\multi-merchant_store\tugas_flask\app\routes\auth.py", line 7, in <module>
#     from app.models import Users
#   File "C:\Users\Anya\OneDrive\Documents\GitHub\multi-merchant_store\tugas_flask\app\models.py", line 5, in <module>
#     from app import db
# ImportError: cannot import name 'db' from 'app' (consider renaming 'C:\\Users\\Anya\\OneDrive\\Documents\\GitHub\\multi-merchant_store\\tugas_flask\\app\\__init__.py' if it has the same name as a library you intended to import)