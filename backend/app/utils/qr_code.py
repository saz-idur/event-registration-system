import qrcode
from io import BytesIO
import re
import logging
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_qr_code_image(data):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, 'PNG')
        logger.info(f"QR code generated for data: {data}")
        return bio.getvalue()
    except Exception as e:
        logger.error(f"Error generating QR code for {data}: {str(e)}")
        raise

def upload_file_to_supabase(file_content, bucket_name, file_name, content_type='image/png'):
    supabase = current_app.supabase
    try:
        if isinstance(file_content, str):
            import base64
            file_content = base64.b64decode(file_content.split(',')[1])
        elif hasattr(file_content, 'read'):
            file_content = file_content.read()
        elif isinstance(file_content, bytes):
            pass
        else:
            raise ValueError('Invalid file content type')

        # Check if file already exists and overwrite if necessary
        supabase.storage.from_(bucket_name).remove([file_name])
        response = supabase.storage.from_(bucket_name).upload(file_name, file_content, {'content-type': content_type})
        if response.status_code == 200 or response.status_code == 201:
            url = f"{current_app.config['SUPABASE_URL']}/storage/v1/object/public/{bucket_name}/{file_name}"
            logger.info(f"File uploaded to Supabase: {url}")
            return url
        else:
            logger.error(f"Upload failed with status {response.status_code}: {response.content}")
            raise ValueError(f'File upload failed: {response.content}')
    except Exception as e:
        logger.error(f"Error uploading to Supabase bucket {bucket_name}/{file_name}: {str(e)}")
        raise

def format_phone_number(phone_number):
    try:
        # Validate and format phone number (Bangladesh-specific)
        if not re.match(r'^(0|\+88)?\d{9,10}$', phone_number):
            raise ValueError('Invalid phone number format (e.g., 01712345678 or +8801712345678)')
        if phone_number.startswith('0'):
            phone_number = '+88' + phone_number[1:]
        elif not phone_number.startswith('+'):
            phone_number = '+880' + phone_number
        logger.debug(f"Formatted phone number: {phone_number}")
        return phone_number
    except Exception as e:
        logger.error(f"Error formatting phone number {phone_number}: {str(e)}")
        raise