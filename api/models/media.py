from api.db import db
from sqlalchemy.dialects.mysql import ENUM
from uuid import uuid4

class Media(db.Model):
    __tablename__ = 'media'
    
    media_id = db.Column(db.String(36), primary_key=True)
    type = db.Column(ENUM('TRIP', 'ITINERARY'), nullable=False)
    trip_id = db.Column(db.String(36), db.ForeignKey('trip.trip_id'), nullable=True)
    itinerary_id = db.Column(db.String(36), db.ForeignKey('itinerary.itinerary_id'), nullable=True)
    path = db.Column(db.String(100), nullable=False)
    upload_datetime = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    def __init__(self, **kwargs):
        self.media_id = str(uuid4())
        self.itinerary_id = kwargs.get('itinerary_id', None)
        self.media_type = kwargs.get('media_type', None)
        self.media_url = kwargs.get('media_url', None)

    # TODO: Complete E2E serving of media_url
    def serialize(self):
        return {
            'media_id': self.media_id,
            'media_url': self.path
        }