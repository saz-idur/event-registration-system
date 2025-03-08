import pytest
import os
from app import create_app
from supabase import create_client
import bcrypt
import time
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
    app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def supabase(app):
    supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
    yield supabase
    # Cleanup after tests (exclude a dummy UUID to avoid deleting all if no data)
    supabase.table('users').delete().neq('user_id', '00000000-0000-0000-0000-000000000000').execute()
    supabase.table('admins').delete().neq('admin_id', '00000000-0000-0000-0000-000000000000').execute()

@pytest.fixture
def admin_token(client, supabase):
    # Setup an admin for JWT authentication
    hashed_password = bcrypt.hashpw('adminpass'.encode('utf-8'), bcrypt.gensalt())
    admin_data = {
        'email': 'admin@test.com',
        'password': hashed_password.decode('utf-8')
    }
    response = supabase.table('admins').insert(admin_data).execute()
    admin_id = response.data[0]['admin_id']

    # Login to get token
    login_response = client.post('/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    assert login_response.status_code == 200, f"Login failed: {login_response.get_data(as_text=True)}"
    token = login_response.get_json()['access_token']
    yield {'Authorization': f'Bearer {token}'}

    # Cleanup admin
    supabase.table('admins').delete().eq('admin_id', admin_id).execute()

def test_full_backend_flow(client, supabase, admin_token):
    # Step 1: Register a user
    user_data = {
        'name': 'Test User',
        'batch': '2023',
        'branch': 'CSE',
        'phone_number': '01712345678',
        'transaction_id': 'TXN123'
    }
    register_response = client.post('/users/register', data=user_data, content_type='multipart/form-data')
    assert register_response.status_code == 201
    user_id = register_response.get_json()['user_id']
    assert user_id is not None

    # Verify user in database
    user = supabase.table('users').select('*').eq('user_id', user_id).execute().data[0]
    assert user['name'] == 'Test User'
    assert user['approval_status'] == 'pending'
    assert user['check_in_status'] == 'not_checked_in'

    # Step 2: Fetch pending users
    pending_response = client.get('/users/pending', headers=admin_token)
    assert pending_response.status_code == 200
    pending_users = pending_response.get_json()
    assert any(u['user_id'] == user_id for u in pending_users)

    # Step 3: Approve user (includes QR code generation and WhatsApp message)
    approve_response = client.patch(f'/users/approve/{user_id}', headers=admin_token)
    assert approve_response.status_code == 200
    assert approve_response.get_json()['message'] == 'User approved and QR code sent'

    # Verify approval and QR code
    updated_user = supabase.table('users').select('*').eq('user_id', user_id).execute().data[0]
    assert updated_user['approval_status'] == 'approved'
    assert updated_user['qr_code_image_url'] is not None
    assert updated_user['qr_code_image_url'].startswith(f"{os.environ['SUPABASE_URL']}/storage/v1/object/public/qr_codes/")

    # Step 4: Scan QR code for check-in
    scan_response = client.post('/qr_codes/scan', json={'user_id': user_id})
    assert scan_response.status_code == 200
    assert scan_response.get_json()['message'] == 'User checked in successfully'

    # Verify check-in status
    checked_in_user = supabase.table('users').select('*').eq('user_id', user_id).execute().data[0]
    assert checked_in_user['check_in_status'] == 'checked_in'

    # Step 5: Attempt to check in again (should fail)
    repeat_scan_response = client.post('/qr_codes/scan', json={'user_id': user_id})
    assert repeat_scan_response.status_code == 400
    assert 'already checked in' in repeat_scan_response.get_data(as_text=True)

    # Step 6: Test WhatsApp manual message (assuming WhatsApp bot is mocked or functional)
    whatsapp_response = client.post(
        '/whatsapp/send_message',
        headers=admin_token,
        json={'phone_number': '+8801712345678', 'message': 'Test message'}
    )
    assert whatsapp_response.status_code == 200
    assert whatsapp_response.get_json()['message'] == 'Message sent successfully'

    # Step 7: Test rejecting a new user
    new_user_data = {
        'name': 'Reject User',
        'batch': '2024',
        'branch': 'EEE',
        'phone_number': '01798765432',
        'transaction_id': 'TXN456'
    }
    new_register_response = client.post('/users/register', data=new_user_data, content_type='multipart/form-data')
    assert new_register_response.status_code == 201
    new_user_id = new_register_response.get_json()['user_id']

    reject_response = client.patch(f'/users/reject/{new_user_id}', headers=admin_token)
    assert reject_response.status_code == 200
    assert reject_response.get_json()['message'] == 'User rejected successfully'

    # Verify rejection
    rejected_user = supabase.table('users').select('*').eq('user_id', new_user_id).execute().data[0]
    assert rejected_user['approval_status'] == 'rejected'

def test_auth(client, supabase):
    # Setup admin
    hashed_password = bcrypt.hashpw('testpass'.encode('utf-8'), bcrypt.gensalt())
    supabase.table('admins').insert({'email': 'test@admin.com', 'password': hashed_password.decode('utf-8')}).execute()

    # Test successful login
    login_response = client.post('/auth/login', json={'email': 'test@admin.com', 'password': 'testpass'})
    assert login_response.status_code == 200
    token = login_response.get_json()['access_token']
    assert token is not None

    # Test protected route
    protected_response = client.get('/auth/protected', headers={'Authorization': f'Bearer {token}'})
    assert protected_response.status_code == 200
    assert 'Hello, admin' in protected_response.get_json()['message']

    # Test invalid login
    invalid_login = client.post('/auth/login', json={'email': 'test@admin.com', 'password': 'wrongpass'})
    assert invalid_login.status_code == 401
    assert 'Invalid credentials' in invalid_login.get_data(as_text=True)