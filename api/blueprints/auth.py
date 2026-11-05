from flask import Blueprint, request, jsonify
from api.models.user import User
from api.db import db
from flask_jwt_extended import (
    create_access_token, verify_jwt_in_request, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies
)
import bcrypt

auth_blueprint = Blueprint('user', __name__, url_prefix='/user')

@auth_blueprint.route('/login', methods=['OPTIONS', 'POST'])
def auth_login():
    match request.method:
        case 'OPTIONS':
            return {}, 200
        
        case 'POST':
            data = request.get_json()
            user =  db.session.query(User).filter(User.username == data.get('username')).first()

            if not user or not user.check_password(data.get('password')):
                return jsonify({ 'status': 'fail' }), 401

            # New login invalidates every token issued before it
            user.token_version = (user.token_version or 0) + 1
            db.session.commit()

            access_token = create_access_token(
                identity=str(user.user_id),
                additional_claims={ 'tv': user.token_version }
            )
            response = jsonify({ 'status': 'success', 'details': { 'username': user.username, 'user_id': user.user_id } })
            set_access_cookies(response, access_token)
            return response, 200

@auth_blueprint.route('/logout', methods=['OPTIONS', 'POST'])
def auth_logout():
    if request.method == 'OPTIONS':
        return {}, 200

    response = jsonify({ 'status': 'success' })
    unset_jwt_cookies(response)
    return response, 200

@auth_blueprint.route('/signup', methods=['OPTIONS', 'POST'])
def auth_signup():
    match request.method:
        case 'OPTIONS':
            return {}, 200
        
        case 'POST':
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            if username and password:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                return jsonify({ 'status': 'success' }), 200
            else:
                return jsonify({ 'status': 'fail' }), 400
            
@auth_blueprint.route('/verify_token', methods = ['OPTIONS', 'POST'])
def verify_token():
    match request.method:
        case 'OPTIONS':
            return '', 200
        
        case 'POST':
            try:
                verify_jwt_in_request()
                return jsonify({ 'status': 'valid', 'user_id': get_jwt_identity() }), 200
            except Exception:
                return jsonify({'status': 'invalid', 'msg': 'Invalid or expired token'}), 401
            
