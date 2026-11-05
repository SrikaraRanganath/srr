from api.db import db
from sqlalchemy.dialects.mysql import TINYINT
from uuid import uuid4
from datetime import datetime

class BookingGuest(db.Model):
    __tablename__ = 'booking_guests'
    
    guest_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email_id = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(TINYINT(unsigned=True), nullable=True)
    type = db.Column(db.String(10), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.booking_id'), nullable=False)

    def __init__(self, **kwargs):
        self.guest_id = kwargs.get('guest_id', str(uuid4()))
        self.name = kwargs.get('name', None)
        self.phone_number = kwargs.get('phone_number', None)
        self.email_id = kwargs.get('email_id', None)
        self.gender = kwargs.get('gender', None)
        self.age = kwargs.get('age', None)
        self.type = kwargs.get('type', None)
        self.booking_id = kwargs.get('booking_id', None)


    def serialize(self):
        return {
            'guest_id': self.guest_id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email_id': self.email_id,
            'gender': self.gender,
            'age': self.age,
            'type': self.type,
            'booking_id': self.booking_id,
        }