from api import create_app
from api.blueprints.trip import trip_blueprint
from api.blueprints.itinerary import itinerary_blueprint
import os

def register_blueprint_with_prefix(app, blueprint) -> None:
    VERSION = os.getenv('API_VERSION', 'v1')
    common_prefix = f"/api/{VERSION}"
    prefix = common_prefix + blueprint.url_prefix
    app.register_blueprint(blueprint, url_prefix=prefix)

app = create_app()
register_blueprint_with_prefix(app, trip_blueprint)
register_blueprint_with_prefix(app, itinerary_blueprint)

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000)) 
    app.run(debug=True, port=PORT)