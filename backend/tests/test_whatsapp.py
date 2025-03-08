import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_send_whatsapp_message(client):
    headers = {'Authorization': 'Bearer your_jwt_token'}
    response = client.post('/whatsapp/send_message', json={
        'phone_number': '+8801712345678',
        'message': 'Test message'
    }, headers=headers)
    assert response.status_code == 200