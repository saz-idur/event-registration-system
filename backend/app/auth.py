from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from .database import get_admin_by_email

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return abort(400, 'Missing email or password')

    admin = get_admin_by_email(email)
    if not admin or admin['password'] != password:  # In production, hash passwords!
        return abort(401, 'Invalid credentials')

    access_token = create_access_token(identity=admin['admin_id'])
    return jsonify({'access_token': access_token})

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_admin_id = get_jwt_identity()
    return jsonify({'message': f'Hello, admin {current_admin_id}'})