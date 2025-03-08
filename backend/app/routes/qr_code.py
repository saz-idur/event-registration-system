from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from ..database import get_user_by_id, check_in_user
from ..utils.qr_code import generate_qr_code_image, upload_file_to_supabase
from flask_jwt_extended import jwt_required

bp = Blueprint('qr_code', __name__, url_prefix='/qr_codes')

@bp.route('/generate/<user_id>', methods=['POST'])
@jwt_required()
def generate_qr_code(user_id):
    user = get_user_by_id(user_id)
    if not user or user['approval_status'] != 'approved':
        return abort(400, 'User not found or not approved')

    # Generate QR code image
    qr_code_image = generate_qr_code_image(user_id)

    # Upload to Supabase storage
    qr_code_url = upload_file_to_supabase(qr_code_image, 'qr_codes', f'{user_id}.png')

    # Update user's qr_code_image_url
    supabase = request.app.supabase
    supabase.table('users').update({'qr_code_image_url': qr_code_url}).eq('user_id', user_id).execute()

    return jsonify({'qr_code_url': qr_code_url})

@bp.route('/scan', methods=['POST'])
def scan_qr_code():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return abort(400, 'Missing user_id')

    user = get_user_by_id(user_id)
    if not user:
        return abort(404, 'User not found')
    if user['approval_status'] != 'approved':
        return abort(400, 'User not approved')
    if user['check_in_status'] == 'checked_in':
        return abort(400, 'User already checked in')

    # Check in the user
    check_in_user(user_id)

    return jsonify({'message': 'User checked in successfully'})