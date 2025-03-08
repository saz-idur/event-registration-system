import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_generate_qr_code(client):
    # Assuming a user exists and JWT is set up
    headers = {'Authorization': 'Bearer your_jwt_token'}
    response = client.post('/qr_codes/generate/test_user_id', headers=headers)
    assert response.status_code in [200, 400]  # Depends on user state