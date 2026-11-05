from api.db import db
from sqlalchemy.dialects.mysql import TINYINT, DECIMAL, ENUM
from uuid import uuid4
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.String(36), primary_key=True)
    trip_id = db.Column(db.String(36), db.ForeignKey('trips.trip_id'), nullable=False)
    booking_datetime = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    phone_number = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(200), nullable=False)
    guest_count = db.Column(TINYINT(unsigned=True), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False)
    payment_mode = db.Column(db.String(10), nullable=False)
    base_amount = db.Column(DECIMAL(10, 2), nullable=False)
    taxes = db.Column(DECIMAL(10, 2), nullable=False)
    handling_charges = db.Column(DECIMAL(10, 2), nullable=False)
    payment_status = db.Column(ENUM('PENDING', 'SUCCESS', 'FAIL'), nullable=False)

    def __init__(self, **kwargs):
        self.booking_id = kwargs.get('booking_id', str(uuid4()))
        self.trip_id = kwargs.get('trip_id', None)
        self.booking_datetime = kwargs.get('booking_datetime', datetime.now())
        self.phone_number = kwargs.get('phone_number', None)
        self.name = kwargs.get('name', None)
        self.email_id = kwargs.get('email_id', None)
        self.guest_count = kwargs.get('guest_count', 0)
        self.transaction_id = kwargs.get('transaction_id', None)
        self.payment_mode = kwargs.get('payment_mode', None)
        self.base_amount = kwargs.get('base_amount', 0.0)
        self.taxes = kwargs.get('taxes', 0.0)
        self.handling_charges = kwargs.get('handling_charges', 0.0)
        self.payment_status = kwargs.get('payment_status', 'PENDING')

    def serialize(self):
        return {
            'booking_id': self.booking_id,
            'trip_id': self.trip_id,
            'booking_datetime': self.booking_datetime.isoformat(),
            'phone_number': self.phone_number,
            'name': self.name,
            'email_id': self.email_id,
            'guest_count': int(self.guest_count),
            'transaction_id': self.transaction_id,
            'payment_mode': self.payment_mode,
            'base_amount': str(self.base_amount),
            'taxes': str(self.taxes),
            'handling_charges': str(self.handling_charges),
            'total_amount': str(self.base_amount + self.taxes + self.handling_charges),
            'payment_status': self.payment_status
        }