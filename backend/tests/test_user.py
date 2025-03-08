import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_register_user(client):
    response = client.post('/users/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'phone_number': '01712345678',
        'payment_proof': (open('test_image.png', 'rb'), 'test_image.png')
    }, content_type='multipart/form-data')
    assert response.status_code == 201
    assert 'user_id' in response.get_json()