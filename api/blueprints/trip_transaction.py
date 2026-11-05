from flask import Blueprint, request, jsonify, current_app
from api.models.trip import Trip
from api.models.itinerary import Itinerary
from api.models.media import Media
from api.db import db
from api.blueprints.media import delete_media
from api.blueprints.itinerary import delete_itinerary
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import datetime
import json

trip_transaction_blueprint = Blueprint('trip_transaction', __name__, url_prefix='/trip_transaction')

@trip_transaction_blueprint.route('/<string:trip_id>', methods=['GET', 'DELETE'])
def get_or_delete_trip_transaction(trip_id):
    match request.method:
        case 'GET':
            res = {
                'basic': {},
                'itinerary': []
            }
            trip = db.session.query(Trip).filter(Trip.trip_id == trip_id).first()
            if trip:
                res['basic'] = trip.serialize()

                trip_itineraries = db.session.query(Itinerary).filter(Itinerary.trip_id == trip_id).order_by(Itinerary.date).all()
                for itinerary in trip_itineraries:
                    itinerary_data = itinerary.serialize()
                    res['itinerary'].append(itinerary_data)

                return jsonify(res), 200
            else:
                return {'error': 'Trip not found'}, 404

        case 'DELETE':
            try:
                trip = db.session.query(Trip).filter(Trip.trip_id == trip_id).first()
                if not trip:
                    return {'error': 'Trip not found'}, 404
                
                db.session.delete(trip)
                db.session.commit()

                cover_image_media = db.session.query(Media).filter(Media.media_id == trip.cover_image).first()
                if cover_image_media and os.path.exists(cover_image_media.path):
                    os.remove(cover_image_media.path)
                    db.session.delete(cover_image_media)
                    
                itineraries = db.session.query(Itinerary).filter(Itinerary.trip_id == trip_id).all()
                for itinerary in itineraries:
                    media_list = itinerary.media_csv.split(',')
                    for media_id in media_list:
                        media = db.session.query(Media).filter(Media.media_id == media_id).first()
                        if media:
                            if os.path.exists(media.path):
                                os.remove(media.path)
                            db.session.delete(media)
                    db.session.delete(itinerary)

                return jsonify({'message': 'Trip deleted successfully'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'status': True, 'error': 'Failed'}), 500

@trip_transaction_blueprint.route('', methods=['OPTIONS', 'POST', 'PUT'])
def add_edit_trip_transaction():
    match request.method:
        case 'OPTIONS':
            return '', 200

        case 'POST':
            basic_trip_details = json.loads(request.form.get('basic'))
            itinerary = json.loads(request.form.get('itinerary'))
            cover_image = request.files.get('cover_image')
            try:
                with db.session.begin(): # Transaction
                    trip = Trip(**basic_trip_details)
                    trip.cover_image = ''
                    db.session.add(trip)
                    db.session.flush()

                    if cover_image:
                        filename = secure_filename(cover_image.filename)
                        save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                        cover_image.save(save_path)                  
                        cover_image_id = uuid4()
                        
                        media = Media(
                            media_id=cover_image_id,
                            type='TRIP',
                            trip_id=trip.trip_id,
                            path=save_path,
                            upload_datetime=datetime.datetime.now()
                        )
                        db.session.add(media)
                        trip.cover_image = str(cover_image_id)

                    for index, item in enumerate(itinerary):
                        itinerary = Itinerary(
                            trip_id=trip.trip_id,
                            title=item['title'],
                            description=item['description'],
                            date=item['date'],
                            media_csv=""
                        )
                        db.session.add(itinerary)
                        db.session.flush()
                        media_list = []

                        for key in request.files:
                            if key.startswith(f'itinerary_{index}_media_'):
                                file = request.files[key]
                                filename = secure_filename(file.filename)
                                save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                                file.save(save_path)

                                media_id = uuid4()
                                media = Media(
                                    media_id=media_id,
                                    type='ITINERARY',
                                    itinerary_id=itinerary.itinerary_id,
                                    path=save_path,
                                    upload_datetime=datetime.datetime.now()
                                )
                                media_list.append(media_id)
                                db.session.add(media)
                                
                        itinerary.media_csv = ",".join([str(media_id) for media_id in media_list])

                    db.session.commit()
                    return jsonify({ 'status': True }), 201

            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify({ 'status': False, 'error': 'Invalid request' }), 500
            
        case 'PUT':
            basic_trip_details = json.loads(request.form.get('basic'))
            itinerary = json.loads(request.form.get('itinerary'))
            cover_image = request.files.get('cover_image')
            delete_itinerary_list = json.loads(request.form.get('deleteItineraryList', '[]'))
            delete_media_list = json.loads(request.form.get('deleteMediaList', '[]'))


            try:
                with db.session.begin(): # Transaction
                    trip = Trip.query.filter(Trip.trip_id == basic_trip_details['trip_id']).first()
                    if not trip:
                        return jsonify({ 'status': False, 'error': 'Trip not found' }), 404
                    for key, value in basic_trip_details.items():
                        if hasattr(trip, key):
                            setattr(trip, key, value)

                    if cover_image and trip.cover_image:
                        media = Media.query.filter(Media.media_id == trip.cover_image).first()
                        if media and os.path.exists(media.path):
                            os.remove(media.path)
                        
                        filename = secure_filename(cover_image.filename)
                        save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                        cover_image.save(save_path)
                        
                        media.path = save_path
                        media.upload_datetime = datetime.datetime.now()

                    # Itinerary deletion -> Delete associated media as well
                    for itinerary_id in delete_itinerary_list:
                        itinerary_item = Itinerary.query.filter(Itinerary.itinerary_id == itinerary_id).first()
                        if itinerary_item:
                            media_list = itinerary_item.media_csv.split(',')
                            for media_id in media_list:
                                media = Media.query.filter(Media.media_id == media_id).first()
                                if media:
                                    if os.path.exists(media.path):
                                        os.remove(media.path)
                                    db.session.delete(media)
                            db.session.delete(itinerary_item)

                    # Media deletion -> Maintain a map of itinerary_id to media_ids for updating itinerary.media_csv later
                    media_itinerary_map = {}
                    for media_id in delete_media_list:
                        media = Media.query.filter(Media.media_id == media_id).first()
                        if media:
                            if os.path.exists(media.path):
                                os.remove(media.path)
                            db.session.delete(media)
                            media_itinerary_map.setdefault(media.itinerary_id, []).append(media_id)

                    for index, item in enumerate(itinerary):
                        is_new_itinerary = not item.get('isOnServer', False)
                        if is_new_itinerary:
                            new_itinerary = Itinerary(
                                trip_id=trip.trip_id,
                                title=item['title'],
                                description=item['description'],
                                date=item['date'],
                                media_csv=''
                            )
                            db.session.add(new_itinerary)
                            db.session.flush()

                            media_list = []
                            for key in request.files:
                                if key.startswith(f'itinerary_{index}_media_'):
                                    file = request.files[key]
                                    filename = secure_filename(file.filename)
                                    save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                                    file.save(save_path)

                                    media_id = uuid4()
                                    media = Media(
                                        media_id=media_id,
                                        type='ITINERARY',
                                        itinerary_id=new_itinerary.itinerary_id,
                                        path=save_path,
                                        upload_datetime=datetime.datetime.now()
                                    )
                                    media_list.append(str(media_id))
                                    db.session.add(media)

                            new_itinerary.media_csv = ",".join(media_list)

                        else:
                            itinerary_item = Itinerary.query.filter(Itinerary.itinerary_id == item['itinerary_id']).first()
                            if not itinerary_item:
                                return jsonify({ 'status': False, 'error': 'Itinerary item not found' }), 404
                            for key, value in item.items():
                                if hasattr(itinerary_item, key):
                                    setattr(itinerary_item, key, value)
                            current_itinerary_media = itinerary_item.media_csv.split(',') if itinerary_item.media_csv else []
                            current_itinerary_media = [mid for mid in current_itinerary_media if mid not in media_itinerary_map.get(itinerary_item.itinerary_id, [])]
                            media_list = []
                            for key in request.files:
                                if key.startswith(f'itinerary_{index}_media_'):
                                    file = request.files[key]
                                    filename = secure_filename(file.filename)
                                    save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                                    file.save(save_path)

                                    media_id = uuid4()
                                    media = Media(
                                        media_id=media_id,
                                        type='ITINERARY',
                                        itinerary_id=new_itinerary.itinerary_id if is_new_itinerary else item['itinerary_id'],
                                        path=save_path,
                                        upload_datetime=datetime.datetime.now()
                                    )
                                    media_list.append(str(media_id))
                                    db.session.add(media)
                            itinerary_item.media_csv = ",".join(current_itinerary_media + media_list)

                    db.session.commit()
                    return jsonify({ 'status': True }), 200

            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify({ 'status': False, 'error': 'Invalid request' }), 500