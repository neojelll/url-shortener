from fastapi.testclient import TestClient
from fastapi import status

from api.api import app, is_valid_url

from unittest.mock import AsyncMock
import pytest


client = TestClient(app)


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los")
	assert not is_valid_url("aldakooaj")
	assert not is_valid_url("")


@pytest.mark.asyncio
async def test_post_request(mocker):
	data = {
		"url": "http://domain.ru/los/hex"
	}

	mock_broker = mocker.patch('api.api.KafkaProducer', autospec=True)
	instance = mock_broker.return_value
	instance.send = AsyncMock()


	response = client.post("/v1/url/shorten", json=data)
	assert response.status_code == status.HTTP_200_OK
	assert "task" in response.json()

	await instance.send("topic_name", data)
	instance.send.assert_awaited()


def test_post_request_error():
	response = client.post(
		"/v1/url/shorten", 
		json={
		"prefix": "inbeer", 
		"expiration": 48
		}
		)
	assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
	assert "detail" in response.json()


def test_get_request():
	response = client.get("/v1/url/shorten")
	assert response.status_code == status.HTTP_200_OK


def test_transport_to_long_url():
	response = client.get("/github.com", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND
