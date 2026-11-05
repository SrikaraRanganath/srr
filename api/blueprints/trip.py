from flask import Blueprint, request, jsonify
from api.models.trip import Trip
from api.models.itinerary import Itinerary
from api.db import db
from api.utils.pagination import paginate_query
import os

trip_blueprint = Blueprint('trip', __name__, url_prefix='/trip')
TRIP_NOT_FOUND = ({'error': 'Trip not found'}, 404)

@trip_blueprint.route('', methods=['GET', 'POST', 'PUT', 'OPTIONS'])
def trip():
    match request.method:
        case 'OPTIONS':
            return '', 200
        case 'GET':
            status = str(request.args.get('status', default=False)).lower() == 'true'
            query = db.session.query(Trip)

            if status:
                active_trips = query.filter(Trip.status == True).all()
                return jsonify([trip.serialize() for trip in active_trips]), 200
            else:
                trips = paginate_query(query)
                return jsonify({
                    "trips": [trip.serialize() for trip in trips['items']],
                    "current_page": trips['current_page'],
                    "per_page": trips['per_page'],
                    "total_pages": trips['total_pages'],
                    "total_items": trips['total_items']
                }), 200
        
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
            

@trip_blueprint.route('/<string:trip_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def get_or_delete_trip(trip_id):
    match request.method:
        case 'OPTIONS':
            return '', 200
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
            

@trip_blueprint.route('/media/<string:trip_id>', methods=['GET'])
def get_trip_media(trip_id):
    trip_itinerary = db.session.query(Itinerary).filter(Itinerary.trip_id == trip_id).all()
    media_links = []
    for itinerary in trip_itinerary:
        media_list = itinerary.media_csv.split(',') if itinerary.media_csv else []
        for media in media_list:
            media_links.append({
                'media_id': media,
                'media_url': f"{request.host_url.rstrip('/')}/api/{os.environ.get('VERSION', 'v1')}/media/{media}"
            })

    if media_links:
        return jsonify(media_links), 200
    else:
        return TRIP_NOT_FOUND