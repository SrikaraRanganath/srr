from unittest import case
from flask import Blueprint, request, jsonify
from api.models.guest import Guest
from api.db import db
from api.services.otp_service import send_otp, verify_otp, resend_otp as resend_otp_service
import httpx

guest_blueprint = Blueprint('guest', __name__, url_prefix='/guest')

@guest_blueprint.route('', methods=['GET', 'OPTIONS', 'POST', 'PUT'])
def get_post_put_guest():
    match request.method:
        case 'GET':
            guests = db.session.query(Guest).all()
            return jsonify([guest.serialize() for guest in guests]), 200
        
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            try:
                data = request.get_json()
                guest = Guest(**data)
                db.session.add(guest)
                db.session.commit()
                return jsonify(guest.serialize()), 201
            except Exception as e:
                db.session.rollback()
                return {'error': "Invalid request"}, 400
        
        case 'PUT':
            data = request.get_json()
            guest = db.session.query(Guest).filter_by(guest_id=data.get('guest_id')).first()
            if not guest:
                return {'error': 'Guest not found'}, 404
            for key, value in data.items():
                setattr(guest, key, value)
            db.session.commit()
            return jsonify(guest.serialize()), 200

@guest_blueprint.route('/<guest_id>', methods=['GET', 'DELETE'])
def get_delete_guest(guest_id):
    match request.method:
        case 'GET':
            guest = db.session.query(Guest).filter_by(guest_id=guest_id).first()
            if not guest:
                return {'error': 'Guest not found'}, 404
            return jsonify(guest.serialize()), 200

        case 'DELETE':
            guest = db.session.query(Guest).filter_by(guest_id=guest_id).first()
            if not guest:
                return {'error': 'Guest not found'}, 404
            db.session.delete(guest)
            db.session.commit()
            return {'message': 'Guest deleted successfully'}, 200

@guest_blueprint.route('/login', methods=['OPTIONS', 'POST'])
async def get_mobile():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            phone_number = request.json.get('phone_number')
            if not phone_number:
                return {'error': 'Phone number is required'}, 400

            guest = db.session.query(Guest).filter(Guest.phone_number == phone_number).first()
            try:
                if not guest:
                    new_guest = Guest(phone_number=phone_number)
                    db.session.add(new_guest)
                    guest = new_guest

                res = await send_otp(mobile=phone_number, type="Login")

                if (type(res) == dict and res.get('type') == 'error'):
                    db.session.rollback()
                    return jsonify({'error': res.get('message')}), 400

                elif res and res.status_code == 200 and res.json().get('type') == 'success':
                    db.session.commit()
                    success_res = guest.serialize()
                    success_res['message'] = 'OTP sent successfully'
                    return jsonify(success_res), 200
                else:
                    return jsonify({'error': res.json().get('message')}), 500

            except httpx.TimeoutException as e:
                return jsonify({'error': 'Service timeout'}), 504
            except httpx.RequestError as e:
                return jsonify({'error': 'Service request failed'}), 502
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500
        
@guest_blueprint.route('/verify', methods=['OPTIONS', 'POST'])
async def verify_mobile():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            phone_number = request.json.get('phone_number')
            otp = request.json.get('otp')

            if not phone_number or not otp or not isinstance(otp, int):
                return {'error': 'Phone number and OTP are required'}, 400
            
            guest = db.session.query(Guest).filter(Guest.phone_number == phone_number).first()
            if not guest:
                return {'error': 'Guest not found'}, 404
            
            try:
                res = await verify_otp(mobile=phone_number, otp=otp)
                if (type(res) == dict and res.get('type') == 'error'):
                    db.session.rollback()
                    return jsonify({'error': res.get('message')}), 400

                elif res and res.status_code == 200 and res.json().get('type') == 'success':
                    success_res = guest.serialize()
                    success_res['message'] = 'OTP verified successfully'
                    return jsonify(success_res), 200
                else:
                    return jsonify({'error': res.json().get('message')}), 400

            except httpx.TimeoutException as e:
                return jsonify({'error': 'Service timeout'}), 504
            except httpx.RequestError as e:
                return jsonify({'error': 'Service request failed'}), 502
            except Exception as e:
                return {'error': str(e)}, 500
            
@guest_blueprint.route('/resend', methods=['OPTIONS', 'POST'])
async def resend_otp():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            phone_number = request.json.get('phone_number')
            if not phone_number:
                return {'error': 'Phone number is required'}, 400
            
            guest = db.session.query(Guest).filter(Guest.phone_number == phone_number).first()
            if not guest:
                return {'error': 'Guest not found'}, 404
            
            try:
                res = await resend_otp_service(mobile=phone_number)
                print(res.json())
                if (type(res) == dict and res.get('type') == 'error'):
                    return jsonify({'error': res.get('message')}), 400

                elif res and res.status_code == 200 and res.json().get('type') == 'success':
                    return jsonify({'message': 'OTP resent successfully'}), 200
                else:
                    return jsonify({'error': res.json().get('message')}), 500

            except httpx.TimeoutException as e:
                return jsonify({'error': 'Service timeout'}), 504
            except httpx.RequestError as e:
                return jsonify({'error': 'Service request failed'}), 502
            except Exception as e:
                return {'error': str(e)}, 500