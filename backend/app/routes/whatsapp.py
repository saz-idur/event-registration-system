from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from flask_jwt_extended import jwt_required
from ..utils.qr_code import format_phone_number
from ..utils.whatsapp import send_whatsapp_message

bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

@bp.route('/send_message', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    phone_number = data.get('phone_number')
    message = data.get('message')

    if not phone_number or not message:
        return abort(400, 'Missing phone_number or message')

    formatted_phone = format_phone_number(phone_number)
    send_whatsapp_message(formatted_phone, message)
    return jsonify({'message': 'Message sent successfully'})