from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from .database import get_admin_by_email
import logging
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return abort(400, description='Missing email or password')

    try:
        admin = get_admin_by_email(email)
        if not admin:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return abort(401, description='Invalid credentials')

        # Verify hashed password
        if not bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
            logger.warning(f"Invalid password attempt for admin: {email}")
            return abort(401, description='Invalid credentials')

        access_token = create_access_token(identity=admin['admin_id'], expires_delta=False)  # No expiration
        logger.info(f"Admin {admin['admin_id']} logged in successfully")
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        logger.error(f"Error during login for {email}: {str(e)}")
        return abort(500, description=f'Login error: {str(e)}')

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_admin_id = get_jwt_identity()
    logger.debug(f"Protected route accessed by admin: {current_admin_id}")
    return jsonify({'message': f'Hello, admin {current_admin_id}'}), 200