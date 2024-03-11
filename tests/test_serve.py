import json
import pytest
from src.serve.serve import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_predict_air(client):
    with open('tests/test_data.json', 'r') as file:
        data = json.load(file)

    response = client.post('/predict', json=data)
    assert response.status_code == 200

    response_data = response.get_json()
    assert 'prediction' in response_data
    assert isinstance(response_data['prediction'], list)
    assert len(response_data['prediction']) == 1
    assert 'prediction' in response_data