from api.db import db
from sqlalchemy.dialects.mysql import TINYINT
from uuid import uuid4
from flask import request
import os

class Testimonial(db.Model):
    __tablename__ = "testimonials"

    testimonial_id = db.Column(db.String(36), primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    trip_id = db.Column(db.String(100), nullable=False)
    customer_photo = db.Column(db.ForeignKey("media.media_id"), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(TINYINT(unsigned=True), nullable=False)
    status = db.Column(db.Boolean)

    def __init__(self, **kwargs):
        self.testimonial_id =  kwargs.get("testimonial_id", str(uuid4()))
        self.customer_name = kwargs.get("customer_name")
        self.trip_id = kwargs.get("trip_id")
        self.customer_photo = kwargs.get("customer_photo")
        self.description = kwargs.get("description")
        self.rating = kwargs.get("rating")
        self.status = kwargs.get("status")

    def serialize(self):
        return {
            "testimonial_id": self.testimonial_id,
            "customer_name": self.customer_name,
            "trip_id": self.trip_id,
            "customer_photo": self.customer_photo,
            "description": self.description,
            "rating": self.rating,
            "customer_photo_url": f"{request.host_url.rstrip('/')}/api/{os.environ.get('VERSION', 'v1')}/media/{self.customer_photo}" if self.customer_photo else None,
            "status": self.status
        }
