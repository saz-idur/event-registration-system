import qrcode
from io import BytesIO

def generate_qr_code_image(data):
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
    return bio.getvalue()

def upload_file_to_supabase(file_content, bucket_name, file_name, content_type='image/png'):
    supabase = current_app.supabase
    if isinstance(file_content, str):
        import base64
        file_content = base64.b64decode(file_content.split(',')[1])
    elif hasattr(file_content, 'read'):
        file_content = file_content.read()
    elif isinstance(file_content, bytes):
        pass
    else:
        raise ValueError('Invalid file content type')

    response = supabase.storage.from_(bucket_name).upload(file_name, file_content, {'content-type': content_type})
    if response.status_code == 200:
        return f"{current_app.config['SUPABASE_URL']}/storage/v1/object/public/{bucket_name}/{file_name}"
    else:
        raise ValueError('File upload failed')

def format_phone_number(phone_number):
    if phone_number.startswith('0'):
        phone_number = '+88' + phone_number[1:]
    elif not phone_number.startswith('+'):
        phone_number = '+880' + phone_number
    return phone_number