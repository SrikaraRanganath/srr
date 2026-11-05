from flask import Blueprint, request, jsonify, current_app
from api.models.testimonial import Testimonial
from api.models.media import Media
from api.models.trip import Trip
from api.db import db
from werkzeug.utils import secure_filename
import json
import os
import datetime
from uuid import uuid4


testimonial_blueprint = Blueprint('testimonial', __name__, url_prefix='/testimonial')

@testimonial_blueprint.route('', methods=['GET', 'OPTIONS', 'POST', 'PUT'])
def get_post_put_testimonials():
    match request.method:
        case 'GET':
            status = str(request.args.get('status', default=False)).lower() == 'true'
            testimonials = []
            if status:
                testimonials = db.session.query(Testimonial).filter(Testimonial.status == True).all()
            
            else:
                testimonials = db.session.query(Testimonial).all()

            testimonials = [testimonial.serialize() for testimonial in testimonials]
            return jsonify(testimonials), 200
        
        case 'OPTIONS':
            return '', 200

        case 'POST':
            data = json.loads(request.form.get('details'))
            customer_photo = request.files.get('customer_photo')
            customer_photo_id = str(uuid4())
            data['customer_photo'] = customer_photo_id
            try:
                with db.session.begin():
                    if customer_photo:
                        filename = secure_filename(customer_photo.filename)
                        save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)
                        customer_photo.save(save_path)
                        
                        media = Media(
                            media_id=str(customer_photo_id),
                            type='TESTIMONIAL',
                            path=save_path,
                            upload_datetime=datetime.datetime.now()
                        )

                        db.session.add(media)
                        db.session.flush()

                    testimonial = Testimonial(**data)
                    db.session.add(testimonial)
                    db.session.commit()

                return jsonify(testimonial.serialize()), 201
            
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify({ 'status': False, 'error': 'Invalid request' }), 500
        
        case 'PUT':
            data = json.loads(request.form.get('details'))
            testimonial = db.session.query(Testimonial).filter_by(testimonial_id=data.get('testimonial_id')).first()
            if not testimonial:
                return {'error': 'Testimonial not found'}, 404
            
            customer_photo = request.files.get('customer_photo')
            if customer_photo:
                filename = secure_filename(customer_photo.filename)
                save_path = os.path.join(current_app.config['MEDIA_FOLDER'], filename)

                media = db.session.query(Media).filter_by(media_id=testimonial.customer_photo).first()

                if media:
                    media.path = save_path

            for key, value in data.items():
                setattr(testimonial, key, value)
            db.session.commit()
            return jsonify(testimonial.serialize()), 200
        
@testimonial_blueprint.route('/<testimonial_id>', methods=['GET', 'DELETE'])
def get_delete_testimonial(testimonial_id):
    match request.method:
        case 'GET':
            testimonial = db.session.query(Testimonial).filter_by(testimonial_id=testimonial_id).first()
            if not testimonial:
                return {'error': 'Testimonial not found'}, 404
            return jsonify(testimonial.serialize()), 200

        case 'DELETE':
            testimonial = db.session.query(Testimonial).filter_by(testimonial_id=testimonial_id).first()
            if not testimonial:
                return {'error': 'Testimonial not found'}, 404
            db.session.delete(testimonial)
            db.session.commit()
            return {'message': 'Testimonial deleted successfully'}, 200