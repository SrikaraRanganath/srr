from api.db import db
from uuid import uuid4

class Itinerary(db.Model):
    __tablename__ = 'itinerary'
    
    itinerary_id = db.Column(db.String(36), primary_key=True)
    trip_id = db.Column(db.String(36), db.ForeignKey('trip.trip_id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    media_csv = db.Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        self.itinerary_id = str(uuid4())
        self.trip_id = kwargs.get('trip_id', None)
        self.title = kwargs.get('title', None)
        self.date = kwargs.get('date', None)
        self.description = kwargs.get('description', None)
        self.media_csv = kwargs.get('media_csv', None)

    def serailize(self):
        return {
            'itinerary_id': self.itinerary_id,
            'trip_id': self.trip_id,
            'title': self.title,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'media_csv': self.media_csv
        }