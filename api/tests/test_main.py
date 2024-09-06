from fastapi.testclient import TestClient
from api.main import app, is_valid_json, is_valid_url


client = TestClient(app)


def test_is_valid_json():
	assert is_valid_json({"name": "surname"}) == False
	assert is_valid_json({"url": "auiaia"}) == True


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los") == True
	assert is_valid_url("aldakooaj") == False
	assert is_valid_url("") == False


def test_post_request():
	response = client.post("/v1/url/shorten", headers={"url": "http://domain.ru/los/hex"})
	assert response.status_code == 200


def test_get_request():
	response = client.get("/v1/url/shorten")
	assert response.status_code == 200


def test_transport_to_long_url():
	response = client.get("/prefix-shorturl", headers={"link": "https://fastapi.tiangolo.com/tutorial/testing/#extended-testing-file"})
	print(response.json())
	assert response.status_code == 302