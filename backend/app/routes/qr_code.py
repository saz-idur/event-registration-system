from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from ..database import get_user_by_id, check_in_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('qr_code', __name__, url_prefix='/qr_codes')

@bp.route('/scan', methods=['POST'])
def scan_qr_code():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return abort(400, description='Missing user_id')

    user = get_user_by_id(user_id)
    if not user:
        return abort(404, description='User not found')
    if user['approval_status'] != 'approved':
        return abort(400, description='User not approved')
    if user['check_in_status'] == 'checked_in':
        return abort(400, description='User already checked in')

    try:
        check_in_user(user_id)
        logger.info(f"User checked in: {user_id}")
        return jsonify({'message': 'User checked in successfully'}), 200
    except Exception as e:
        logger.error(f"Error checking in user {user_id}: {str(e)}")
        return abort(500, description=f'Error checking in user: {str(e)}')