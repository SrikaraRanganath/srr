from flask import Blueprint, request, jsonify
from api.models.itinerary import Itinerary
from api.db import db

itinerary_blueprint = Blueprint('itinerary', __name__, url_prefix='/itinerary')
ITINERARY_NOT_FOUND = ({'error': 'Itinerary not found'}, 404)

@itinerary_blueprint.route('/', methods=['GET', 'POST', 'PUT'])
def create_or_update_itinerary():
    match request.method:
        case 'GET':
            query_params = request.args.to_dict()
            if query_params:
                query = Itinerary.query
                for key, value in query_params.items():
                    if hasattr(Itinerary, key):
                        query = query.filter(getattr(Itinerary, key) == value)
                itineraries = query.all()
                return jsonify([itinerary.serialize() for itinerary in itineraries]), 200
            else:
                return {'error': 'Invalid request'}, 400
        case 'POST':
            new_itinerary = Itinerary(**request.json)
            db.session.add(new_itinerary)
            db.session.commit()
            return jsonify(new_itinerary.serialize()), 201
        case 'PUT':
            itinerary_id = request.json.get('itinerary_id')
            itinerary = db.session.query(Itinerary).filter(Itinerary.itinerary_id == itinerary_id).first()
            if itinerary:
                for key, value in request.json.items():
                    if hasattr(itinerary, key):
                        setattr(itinerary, key, value)
                db.session.commit()
                return jsonify(itinerary.serialize()), 200
            else:
                return ITINERARY_NOT_FOUND
            
@itinerary_blueprint.route('/<string:itinerary_id>', methods=['GET', 'DELETE'])
def get_or_delete_itinerary(itinerary_id):
    match request.method:
        case 'GET':
            itinerary = db.session.query(Itinerary).filter(Itinerary.itinerary_id == itinerary_id).first()
            if itinerary:
                return jsonify(itinerary.serialize()), 200
            else:
                return ITINERARY_NOT_FOUND

        case 'DELETE':
            itinerary = db.session.query(Itinerary).filter(Itinerary.itinerary_id == itinerary_id).first()
            if itinerary:
                db.session.delete(itinerary)
                db.session.commit()
                return jsonify({"message": "Itinerary deleted successfully"}), 200
            else:
                return ITINERARY_NOT_FOUND
        