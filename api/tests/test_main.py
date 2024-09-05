from fastapi.testclient import TestClient
from api.main import app, is_valid_json, is_valid_url
import pytest

client = TestClient(app)

def test_is_valid_json():
	assert is_valid_json({"name": "surname"}) == False
	assert is_valid_json({"url": "auiaia"}) == True


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los") == True
	assert is_valid_url("aldakooaj") == False
	assert is_valid_url("") == False


def test_post_request():
	response = client.post("v1/url/shorten", headers={"url": "http://domain.ru/los/hex"})
	assert response.status_code == 200
	assert response.json() == {"Task": "aokx0q-923nd-adalas"}