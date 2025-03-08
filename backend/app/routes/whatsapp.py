from flask import Blueprint, request, jsonify
from werkzeug.exceptions import abort
from flask_jwt_extended import jwt_required
from ..utils.qr_code import format_phone_number
from ..utils.whatsapp import send_whatsapp_message
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

@bp.route('/send_message', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    phone_number = data.get('phone_number')
    message = data.get('message')

    if not phone_number or not message:
        return abort(400, description='Missing phone_number or message')

    try:
        formatted_phone = format_phone_number(phone_number)
        send_whatsapp_message(formatted_phone, message)
        logger.info(f"Manual message sent to {formatted_phone}")
        return jsonify({'message': 'Message sent successfully'}), 200
    except ValueError as e:
        logger.error(f"Invalid phone number format: {str(e)}")
        return abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error sending manual WhatsApp message: {str(e)}")
        return abort(500, description=f'Error sending message: {str(e)}')