from flask import Blueprint, request, jsonify
from flask import render_template
from api.models.booking import Booking
from api.models.trip import Trip
from api.models.booking_guest import BookingGuest
from api.services.razorpay_service import create_order as create_razorpay_order, verify_order as verify_razorpay_order
from api.utils.email import send_email_async
from api.db import db
from datetime import datetime
import os

payment_blueprint = Blueprint("payment", __name__, url_prefix="/payment")

def validate_create_order_request(req_body):
    if not req_body:
        return False
    
    if not isinstance(req_body, dict):
        return False

    if isinstance(req_body, dict):
        # Validate amount field
        if "amount" not in req_body or not isinstance(req_body["amount"], int) or req_body["amount"] <= 0:
            return False

        if "receipt" in req_body and (not isinstance(req_body["receipt"], str) or not req_body["receipt"].strip()):
            return False
        
        if "notes" in req_body:
            if not isinstance(req_body["notes"], dict):
                return False
            if len(req_body["notes"]) > 15 or any(len(str(k)) > 256 or len(str(v)) > 256 for k, v in req_body["notes"].items()):
                return False
            
        return True

def validate_verify_order_request(req_body):
    if not req_body:
        return False
    
    if not isinstance(req_body, dict):
        return False

    if isinstance(req_body, dict):
        # Validate order_id field
        if "razorpay_order_id" not in req_body or not isinstance(req_body["razorpay_order_id"], str) or not req_body["razorpay_order_id"].strip():
            return False

        # Validate payment_id field
        if "razorpay_payment_id" not in req_body or not isinstance(req_body["razorpay_payment_id"], str) or not req_body["razorpay_payment_id"].strip():
            return False
        
        # Validate signature field
        if "razorpay_signature" not in req_body or not isinstance(req_body["razorpay_signature"], str) or not req_body["razorpay_signature"].strip():
            return False
        
        # Validate booking_id field
        if "booking_id" not in req_body or not isinstance(req_body["booking_id"], str) or not req_body["booking_id"].strip():
            return False
        
        return True

@payment_blueprint.route("/create_order", methods=["OPTIONS", "POST"])
def create_order():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            data = request.get_json()

            try:
                if not validate_create_order_request(data):
                    return jsonify({"error": "Invalid request"}), 400
                
                order = create_razorpay_order(amount=data["amount"], receipt=data.get("receipt", ""), notes=data.get("notes", {}))
                return jsonify(order), 200
            except Exception as e:
                return jsonify({"error": "Invalid request"}), 500
            
@payment_blueprint.route("/verify_order", methods=["OPTIONS", "POST"])
def verify_order():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            data = request.get_json()
            if not validate_verify_order_request(data):
                return jsonify({"error": "Invalid request"}), 400


            (booking, trip) = db.session.query(Booking, Trip).join(Trip, Trip.trip_id==Booking.trip_id).filter(Booking.booking_id==data["booking_id"]).first()

            # Idempotency check - DO NOT PROCESS TWICE
            if booking.payment_status in ('SUCCESS', 'FAIL'):
                return jsonify({ "status": booking.payment_status.lower() }), 200

            is_order_valid = verify_razorpay_order(data["razorpay_order_id"], data["razorpay_payment_id"], data["razorpay_signature"])
            booking.transaction_id=data["razorpay_order_id"]
            
            if is_order_valid:
                # Update booking table
                booking.payment_status="SUCCESS"
                db.session.commit()

                # Send confirmation email
                guests = db.session.query(BookingGuest).filter(BookingGuest.booking_id==booking.booking_id).all()

                if booking:
                    html_content = render_template(
                        "booking_confirmation.html",
                        logo_url=os.getenv('MAIL_LOGO_URL', ''),
                        company_name="Sri Rajarajeshwari Tours and Travels",
                        primary_guest_name=booking.name,
                        title=trip.title,
                        start_date=trip.start_date.strftime("%d-%b-%Y"),
                        end_date=trip.end_date.strftime("%d-%b-%Y"),
                        total_guests=booking.guest_count,
                        guests=guests,
                        base_amount=booking.base_amount,
                        taxes=booking.taxes,
                        handling_charges=booking.handling_charges,
                        total_amount=booking.base_amount + booking.taxes + booking.handling_charges,
                        year=datetime.now().year
                    )

                    send_email_async(booking.email_id, "Booking Confirmation", html_content, True)
                    
                return jsonify({"status": "valid"}), 200
            
            else:
                booking.payment_status="FAIL"
                
                (db.session.query(Trip)
                    .filter(Trip.trip_id == trip.trip_id)
                    .update({
                        Trip.current_capacity: Trip.current_capacity + booking.guest_count
                    })
                )
                db.session.commit()
                return jsonify({"status": "invalid"}), 400