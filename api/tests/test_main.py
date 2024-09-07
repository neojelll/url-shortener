from fastapi.testclient import TestClient
from api.main import app, is_valid_url


client = TestClient(app)


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los") == True
	assert is_valid_url("aldakooaj") == False
	assert is_valid_url("") == False


def test_post_request():
	response = client.post("/v1/url/shorten", json={"url": "http://domain.ru/los/hex"})
	assert response.status_code == 200
	assert "Task" in response.json()


def test_post_request_error():
	response = client.post(
		"/v1/url/shorten", 
		json={
		"prefix": "inbeer", 
		"expiration": 48
		}
		)
	assert response.status_code == 422
	assert "detail" in response.json()


def test_get_request():
	response = client.get("/v1/url/shorten")
	assert response.status_code == 200


def test_transport_to_long_url():
	response = client.get("/prefix_osjkcso")
	assert response.status_code == 302