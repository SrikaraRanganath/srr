from flask import Blueprint, request, jsonify
from api.models.itinerary import Itinerary
from api.blueprints.media import delete_media as delete_media_func
from api.db import db

itinerary_blueprint = Blueprint('itinerary', __name__, url_prefix='/itinerary')
ITINERARY_NOT_FOUND = ({'error': 'Itinerary not found'}, 404)

@itinerary_blueprint.route('', methods=['GET', 'POST', 'PUT'])
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
            delete_media = request.args.get('delete_media', 'false').lower() == 'true'
            result = delete_itinerary(itinerary_id, delete_media)
            if result is True:
                return jsonify({'status': 'success'}), 200
            elif result == ITINERARY_NOT_FOUND:
                return ITINERARY_NOT_FOUND
            else:
                return jsonify({'status': 'fail'}), 500

def delete_itinerary(itinerary_id, delete_media=False):
    itinerary = db.session.query(Itinerary).filter(Itinerary.itinerary_id == itinerary_id).first()
    try:
        if itinerary:
            if delete_media and itinerary.media_csv:
                media = itinerary.media_csv.split(',')
                for media_id in media:
                    delete_media_func(media_id)
            else:
                db.session.delete(itinerary)
                db.session.commit()
            return True
        else:
            return ITINERARY_NOT_FOUND
        
    except Exception as e:
        return False
        