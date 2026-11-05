from flask import Blueprint, request, jsonify
from api.models.booking import Booking
from api.models.trip import Trip
from api.db import db
from api.utils.pagination import paginate_query
from datetime import datetime, time

booking_blueprint = Blueprint('booking', __name__, url_prefix='/booking')

@booking_blueprint.route('', methods=['GET', 'OPTIONS', 'POST', 'PUT'])
def get_post_put_booking():
    match request.method:
        case 'GET':
            query = db.session.query(Booking, Trip).join(Trip, Booking.trip_id==Trip.trip_id)
            trip = request.args.get('trip')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            name = request.args.get('name')
            phone_number = request.args.get('phone_number')

            if trip:
                query = query.filter(Trip.title.ilike(f"%{trip}%"))

            if name:
                query = query.filter(Booking.name.ilike(f"%{name}%"))

            if phone_number:
                query = query.filter(Booking.phone_number == phone_number)

            if start_date:
                start_dt = datetime.combine(
                    datetime.strptime(start_date, "%Y-%m-%d").date(),
                    time.min
                )
                query = query.filter(
                    Booking.booking_datetime >= start_dt
                )

            if end_date:
                end_dt = datetime.combine(
                    datetime.strptime(end_date, "%Y-%m-%d").date(),
                    time.max
                )
                query = query.filter(
                    Booking.booking_datetime <= end_dt
                )

            query = query.order_by(Booking.booking_datetime.desc())

            results = paginate_query(query)
            bookings = []
            for booking, trip in results['items']:
                booking_data = booking.serialize()
                booking_data['trip'] = trip.title
                bookings.append(booking_data)

            return jsonify({
                "bookings": bookings,
                "current_page": results['current_page'],
                "per_page": results['per_page'],
                "total_pages": results['total_pages'],
                "total_items": results['total_items']
            }), 200
        
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            try:
                data = request.get_json()
                
                # Atomic Update to prevent overbooking
                rows_updated = (
                    db.session.query(Trip)
                    .filter(
                        Trip.trip_id == data.get('trip_id'),
                        Trip.current_capacity >= int(data.get('guest_count', 0))
                    )
                    .update({
                        Trip.current_capacity: Trip.current_capacity - data.get('guest_count', 0)
                    })
                )

                if rows_updated == 0:
                    db.session.rollback()
                    return jsonify({'error': 'Not enough available slots'}), 409
                
                booking = Booking(**data)
                db.session.add(booking)
                db.session.commit()
                return jsonify(booking.serialize()), 201

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400

        case 'PUT':
            try:
                data = request.get_json()

                booking = db.session.query(Booking).filter_by(
                    booking_id=data.get('booking_id')
                ).first()

                if not booking:
                    return {'error': 'Booking not found'}, 404

                for key, value in data.items():
                    if key != 'booking_id':
                        setattr(booking, key, value)

                db.session.commit()
                return jsonify(booking.serialize()), 200

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 400

@booking_blueprint.route('/<booking_id>', methods=['GET', 'DELETE'])
def get_delete_booking(booking_id):
    match request.method:
        case 'GET':
            booking = db.session.query(Booking).filter_by(booking_id=booking_id).first()
            if not booking:
                return {'error': 'Booking not found'}, 404
            return jsonify(booking.serialize()), 200

        case 'DELETE':
            booking = db.session.query(Booking).filter_by(booking_id=booking_id).first()
            if not booking:
                return {'error': 'Booking not found'}, 404
            db.session.delete(booking)
            db.session.commit()
            return {'message': 'Booking deleted successfully'}, 200
        

@booking_blueprint.route('/trip/<trip_id>', methods=['GET'])
def get_bookings_by_trip(trip_id):
    results = paginate_query(db.session.query(Booking).filter_by(trip_id=trip_id))
    return jsonify({
        "bookings": [booking.serialize() for booking in results['items']],
        "current_page": results['current_page'],
        "per_page": results['per_page'],
        "total_pages": results['total_pages'],
        "total_items": results['total_items']
    }), 200