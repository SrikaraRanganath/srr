from api.db import db
from uuid import uuid4
from sqlalchemy.dialects.mysql import TINYINT, SMALLINT, DECIMAL

class Trip(db.Model):
    __tablename__ = 'Trips'

    trip_id = db.Column(db.String(36), primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    highlights = db.Column(db.Text, nullable=True)
    about = db.Column(db.Text, nullable=True)
    inclusions = db.Column(db.Text, nullable=True)
    exclusions = db.Column(db.Text, nullable=True)
    things_to_carry = db.Column(db.Text, nullable=True)
    price_per_head = db.Column(DECIMAL(10, 2), nullable=False)
    max_capacity = db.Column(SMALLINT(unsigned=True), nullable=False)
    current_capacity = db.Column(SMALLINT(unsigned=True), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    duration = db.Column(TINYINT(unsigned=True), nullable=False)
    features = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        self.trip_id = str(uuid4())
        self.title = kwargs.get('title', None)
        self.destination = kwargs.get('destination', None)
        self.highlights = kwargs.get('highlights', None)
        self.about = kwargs.get('about', None)
        self.inclusions = kwargs.get('inclusions', None)
        self.exclusions = kwargs.get('exclusions', None)
        self.things_to_carry = kwargs.get('things_to_carry', None)
        self.price_per_head = kwargs.get('price_per_head', 0.0)
        self.max_capacity = kwargs.get('max_capacity', 0)
        self.current_capacity = kwargs.get('current_capacity', 0)
        self.start_date = kwargs.get('start_date', None)
        self.end_date = kwargs.get('end_date', None)
        self.duration = kwargs.get('duration', 0)
        self.features = kwargs.get('features', None)
    
    def serialize(self):
        return {
            'trip_id': self.trip_id,
            'title': self.title,
            'destination': self.destination,
            'highlights': self.highlights,
            'about': self.about,
            'inclusions': self.inclusions,
            'exclusions': self.exclusions,
            'things_to_carry': self.things_to_carry,
            'price_per_head': self.price_per_head,
            'max_capacity': self.max_capacity,
            'current_capacity': self.current_capacity,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'duration': self.duration,
            'features': self.features
        }