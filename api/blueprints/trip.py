from flask import Blueprint, request, jsonify
from api.models.trip import Trip
from api.db import db

trip_blueprint = Blueprint('trip', __name__, url_prefix='/trip')
TRIP_NOT_FOUND = ({'error': 'Trip not found'}, 404)

@trip_blueprint.route('/', methods=['GET', 'POST', 'PUT'])
def trip():
    match request.method:
        case 'GET':
            trips = db.session.query(Trip).all()
            return jsonify([trip.serialize() for trip in trips]), 200
        
        case 'POST':
            data = request.json
            new_trip = Trip(**data)
            db.session.add(new_trip)
            db.session.commit()
            return jsonify(new_trip.serialize()), 201
        
        case 'PUT':
            trip_id = request.json.get('trip_id')
            trip = db.session.query(Trip).filter(Trip.trip_id == trip_id).first()
            if trip:
                for key, value in request.json.items():
                    if hasattr(trip, key):
                        setattr(trip, key, value)
                db.session.commit()
                return jsonify(trip.serialize()), 200
            else:
                return TRIP_NOT_FOUND
            

@trip_blueprint.route('/<string:trip_id>', methods=['GET', 'DELETE'])
def get_or_delete_trip(trip_id):
    match request.method:
        case 'GET':
            trip = db.session.query(Trip).filter(Trip.trip_id == trip_id).first()
            if trip:
                return jsonify(trip.serialize()), 200
            else:
                return TRIP_NOT_FOUND

        case 'DELETE':
            trip = db.session.query(Trip).filter(Trip.trip_id == trip_id).first()
            if trip:
                db.session.delete(trip)
                db.session.commit()
                return jsonify({"message": "Trip deleted successfully"}), 200
            else:
                return TRIP_NOT_FOUND