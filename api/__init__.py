from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from api.db import init_db, db
from flask_jwt_extended import JWTManager
from api.mail import init_mail
from datetime import timedelta
import os

load_dotenv()

def env_bool(name, default):
    return os.getenv(name, str(default)).lower() == 'true'

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_DATABASE_URL', '')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '')
    # Token travels in an HttpOnly cookie; CSRF double-submit protects unsafe methods
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = env_bool('JWT_COOKIE_SECURE', True)  # set false for local http
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_EXPIRY_MINUTES', 60)))
    app.config['MEDIA_FOLDER'] = os.path.join(app.root_path, os.environ.get('MEDIA_FOLDER', 'media'))
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER','')

    origins = [o.strip() for o in os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',') if o.strip()]
    CORS(app, origins=origins, supports_credentials=True)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):
        # A newer login bumps users.token_version, which invalidates older tokens
        from api.models.user import User
        user = db.session.get(User, jwt_payload['sub'])
        revoked = user is None or user.token_version != jwt_payload.get('tv')
        # Read-only lookup: end the autobegun transaction so handlers that call
        # `with db.session.begin()` don't hit "A transaction is already begun".
        db.session.rollback()
        return revoked

    init_db(app)
    init_mail(app)

    return app