from api import create_app
from api.blueprints.trip import trip_blueprint
from api.blueprints.itinerary import itinerary_blueprint
from api.blueprints.trip_transaction import trip_transaction_blueprint
from api.blueprints.media import media_blueprint
from api.blueprints.booking import booking_blueprint
from api.blueprints.booking_guest import booking_guest_blueprint
from api.blueprints.testimonials import testimonial_blueprint
from api.blueprints.auth import auth_blueprint
from api.blueprints.guest import guest_blueprint
from api.blueprints.payment import payment_blueprint
from flask_jwt_extended import verify_jwt_in_request
from jwt import ExpiredSignatureError
from flask import request, jsonify
import os

VERSION = os.getenv('API_VERSION', 'v1')
AUTH_REQUIRED = os.getenv('AUTH_REQUIRED', 'true').lower() == 'true'
api_common_prefix = f"/api/{VERSION}"
auth_common_prefix = "/auth"

PROTECTED_METHODS = {
    "trip": ["POST", "PUT", "DELETE"],
    "itinerary": ["POST", "PUT", "DELETE"],
    "booking_guest": ["PUT", "DELETE"],
    "booking": ["DELETE"],
    "guest": ["PUT","DELETE"],
    "media": ["DELETE"],
    "payment": ["PUT", "DELETE"],
    "testimonial": ["POST", "PUT", "DELETE"],
    "trip_transaction": ["POST", "PUT", "DELETE"]
}

def register_blueprint_with_prefix_and_auth(app, blueprint, common_prefix) -> None:
    prefix = common_prefix + blueprint.url_prefix

    if AUTH_REQUIRED:
        @blueprint.before_request
        def require_jwt():
            # Always allow preflight
            if request.method == "OPTIONS" or blueprint.name == "user":
                return
            
            # Apply auth only for protected methods
            if request.method in PROTECTED_METHODS[blueprint.name]:
                try:
                    verify_jwt_in_request()
                except ExpiredSignatureError:
                    return jsonify({"error": "Unauthorized", "message": "Token has expired"}), 401
                except Exception:
                    return jsonify({"error": "Unauthorized", "message": "Invalid or missing token"}), 401

    app.register_blueprint(blueprint, url_prefix=prefix)

app = create_app()
# API Routes
register_blueprint_with_prefix_and_auth(app, trip_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, itinerary_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, trip_transaction_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, media_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, booking_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, booking_guest_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, testimonial_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, guest_blueprint, api_common_prefix)
register_blueprint_with_prefix_and_auth(app, payment_blueprint, api_common_prefix)

# AUTH Route
register_blueprint_with_prefix_and_auth(app, auth_blueprint, auth_common_prefix)

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000)) 
    app.run(debug=True, port=PORT)