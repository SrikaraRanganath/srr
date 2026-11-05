from api.db import db
from uuid import uuid4
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    token_version = db.Column(db.Integer, nullable=False, default=0, server_default='0')

    def __init__(self, username, password):
        self.user_id = uuid4()
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def serialize(self):
        return {
            'user_id': str(self.user_id),
            'username': self.username
        }
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))