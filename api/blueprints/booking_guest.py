from flask import Blueprint, request, jsonify
from api.models.booking import Booking
from api.models.booking_guest import BookingGuest
from api.db import db

booking_guest_blueprint = Blueprint('booking_guest', __name__, url_prefix='/booking_guest')

@booking_guest_blueprint.route('', methods=['GET', 'OPTIONS', 'POST', 'PUT'])
def get_post_put_booking():
    match request.method:
        case 'GET':
            results = db.session.query(Booking, BookingGuest).join(BookingGuest, Booking.booking_id == BookingGuest.booking_id).all()
            bookings = []
            for booking, booking_guest in results:
                booking_data = booking.serialize()
                booking_data['guests'] = booking_guest.serialize()
                bookings.append(booking_data)

            return jsonify(bookings), 200
        
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            try:
                data = request.get_json()
                guests = []
                for guest in data:
                    booking = BookingGuest(**guest)
                    db.session.add(booking)

                    booking_guest = db.session.query(Booking).filter(Booking.booking_id == guest.get('booking_id')).first()
                    if not booking_guest:
                        return jsonify({'error': 'Invalid request'}), 400

                    guests.append(booking.serialize())

                db.session.commit()
                return jsonify(guests), 201

            except Exception as e:
                print(e)
                db.session.rollback()
                return {'error': 'Failed to create booking'}, 400

        case 'PUT':
            data = request.get_json()
            booking = db.session.query(Booking).filter_by(booking_id=data.get('booking_id')).first()
            if not booking:
                return {'error': 'Booking not found'}, 404
            
            for key, value in data.items():
                setattr(booking, key, value)
            db.session.commit()
            return jsonify(booking.serialize()), 200

@booking_guest_blueprint.route('/<booking_id>', methods=['GET', 'DELETE'])
def get_delete_booking(booking_id):
    match request.method:
        case 'GET':
            booking = db.session.query(Booking).filter_by(booking_id=booking_id).first()
            if not booking:
                return {'error': 'Booking not found'}, 404
            
            results = db.session.query(Booking, BookingGuest).filter_by(booking_id=booking_id).join(BookingGuest, Booking.booking_id == BookingGuest.booking_id).all()
            guests_list = []
            for booking, booking_guest in results:
                guests_list.append(booking_guest.serialize())

            return jsonify(guests_list), 200

        case 'DELETE':
            try:
                booking = db.session.query(Booking).filter_by(booking_id=booking_id).first()
                if not booking:
                    return {'error': 'Booking not found'}, 404
                
                booking_guests = db.session.query(BookingGuest).filter(BookingGuest.booking_id == booking_id).all()
                for guest in booking_guests:
                    db.session.delete(guest)

                db.session.commit()
                return {'message': 'Booking deleted successfully'}, 200
            
            except Exception as e:
                db.session.rollback()
                return {'error': 'Failed to delete booking'}, 400