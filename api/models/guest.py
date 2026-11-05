from api.db import db
from uuid import uuid4

class Guest(db.Model):
    __tablename__ = 'guests'

    guest_id = db.Column(db.String(36), primary_key=True)
    fullname = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False, unique=True)
    email_id = db.Column(db.String(250), unique=True, nullable=True)

    def __init__(self, **kwargs):
        self.guest_id = kwargs.get('guest_id', str(uuid4()))
        self.fullname = kwargs.get('fullname')
        self.email_id = kwargs.get('email_id')
        self.phone_number = kwargs.get('phone_number')

    def serialize(self):
        return {
            'guest_id': self.guest_id,
            'fullname': self.fullname,
            'email_id': self.email_id,
            'phone_number': self.phone_number
        }