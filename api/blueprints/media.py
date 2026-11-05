from flask import Blueprint, jsonify, send_from_directory, current_app, abort, request
from api.models.media import Media
from api.db import db
import os

media_blueprint = Blueprint('media', __name__, url_prefix='/media')
MEDIA_NOT_FOUND = ({'error': 'Media not found'}, 404)

@media_blueprint.route('/<string:media_id>', methods=['GET'])
def serve_media(media_id):
    try:
        media = db.session.query(Media).filter(Media.media_id == media_id).first()
        if not media:
            return MEDIA_NOT_FOUND

        if not os.path.exists(media.path):
            return jsonify({'error': 'Media file does not exist'}), 404

        download = request.args.get('download', 'false').lower() == 'true'

        return send_from_directory(directory=current_app.config['MEDIA_FOLDER'], path=os.path.basename(media.path), as_attachment=download)

    except FileNotFoundError:
        abort(404, description="File not found")

@media_blueprint.route('/<string:media_id>', methods=['DELETE'])
def delete_media(media_id):
    try:
        media = db.session.query(Media).filter(Media.media_id == media_id).first()
        if not media:
            return MEDIA_NOT_FOUND

        if os.path.exists(media.path):
            os.remove(media.path)

        db.session.delete(media)
        db.session.commit()

        return jsonify({'message': 'Media deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    