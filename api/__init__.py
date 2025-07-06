from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from api.db import init_db
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_DATABASE_URL', '')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    init_db(app)

    return app