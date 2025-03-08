from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from flask_jwt_extended import jwt_required
from ..database import get_user_by_id, approve_user, get_pending_users
from ..utils.qr_code import generate_qr_code_image, upload_file_to_supabase, format_phone_number
from ..utils.whatsapp import send_whatsapp_message
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('user', __name__, url_prefix='/users')

# Register a new user
@bp.route('/register', methods=['POST'])
def register_user():
    data = request.form
    name = data.get('name')
    batch = data.get('batch')
    branch = data.get('branch')
    phone_number = data.get('phone_number')
    transaction_id = data.get('transaction_id')

    if not all([name, batch, branch, phone_number, transaction_id]):
        return abort(400, description='Missing required fields: name, batch, branch, phone_number, or transaction_id')

    # Validate phone number (Bangladesh-specific)
    if not re.match(r'^(0|\+88)\d{9,10}$', phone_number):
        return abort(400, description='Invalid phone number format (e.g., 01712345678 or +8801712345678)')

    supabase = request.app.supabase
    try:
        user = supabase.table('users').insert({
            'name': name,
            'batch': batch,
            'branch': branch,
            'phone_number': phone_number,
            'transaction_id': transaction_id,
            'approval_status': 'pending',
            'check_in_status': 'not_checked_in'
        }).execute()
        logger.info(f"User registered: {user.data[0]['user_id']}")
        return jsonify({'message': 'User registered successfully', 'user_id': user.data[0]['user_id']}), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return abort(500, description=f'Error registering user: {str(e)}')

# Get all pending users (admin-only)
@bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_users_route():
    try:
        users = get_pending_users()
        logger.info(f"Fetched {len(users)} pending users")
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error fetching pending users: {str(e)}")
        return abort(500, description=f'Error fetching pending users: {str(e)}')

# Approve a user and send QR code via WhatsApp (admin-only)
@bp.route('/approve/<user_id>', methods=['PATCH'])
@jwt_required()
def approve_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return abort(404, description='User not found')
    if user['approval_status'] != 'pending':
        return abort(400, description='User already processed')

    try:
        qr_code_image = generate_qr_code_image(user_id)
        qr_code_url = upload_file_to_supabase(qr_code_image, 'qr_codes', f'{user_id}.png')
    except Exception as e:
        logger.error(f"Error generating/uploading QR code for {user_id}: {str(e)}")
        return abort(500, description=f'Error generating QR code: {str(e)}')

    supabase = request.app.supabase
    try:
        supabase.table('users').update({
            'approval_status': 'approved',
            'qr_code_image_url': qr_code_url
        }).eq('user_id', user_id).execute()
    except Exception as e:
        logger.error(f"Error updating user status for {user_id}: {str(e)}")
        return abort(500, description=f'Error updating user status: {str(e)}')

    formatted_phone = format_phone_number(user['phone_number'])
    message = f"Dear {user['name']}, your registration for the iftar event has been approved. Please present your QR code at the entrance: {qr_code_url}"
    try:
        send_whatsapp_message(formatted_phone, message)
        logger.info(f"Approval message sent to {formatted_phone}")
    except Exception as e:
        logger.warning(f"Failed to send WhatsApp message to {formatted_phone}: {str(e)}")
        # Continue even if WhatsApp fails

    return jsonify({'message': 'User approved and QR code sent'}), 200

# Reject a user (admin-only)
@bp.route('/reject/<user_id>', methods=['PATCH'])
@jwt_required()
def reject_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return abort(404, description='User not found')
    if user['approval_status'] != 'pending':
        return abort(400, description='User already processed')

    supabase = request.app.supabase
    try:
        supabase.table('users').update({'approval_status': 'rejected'}).eq('user_id', user_id).execute()
    except Exception as e:
        logger.error(f"Error rejecting user {user_id}: {str(e)}")
        return abort(500, description=f'Error rejecting user: {str(e)}')

    formatted_phone = format_phone_number(user['phone_number'])
    message = f"Dear {user['name']}, your registration for the iftar event has been rejected. Please contact support for details."
    try:
        send_whatsapp_message(formatted_phone, message)
        logger.info(f"Rejection message sent to {formatted_phone}")
    except Exception as e:
        logger.warning(f"Failed to send rejection message to {formatted_phone}: {str(e)}")
        # Continue even if WhatsApp fails

    return jsonify({'message': 'User rejected successfully'}), 200