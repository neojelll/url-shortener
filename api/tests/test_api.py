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

	mock_broker = mocker.patch('api.api.MessageBroker', autospec=True)
	mock_broker.send = AsyncMock()


	response = client.post("/v1/url/shorten", json=data)
	assert response.status_code == status.HTTP_200_OK
	assert "task" in response.json()

	await mock_broker.send("topic_name", data)
	mock_broker.send.assert_awaited()


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


@pytest.mark.asyncio
async def test_transport_to_long_url(mocker):
	short_url = "github.com"
	long_url = "http://github.com/neojelll/shotener"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)

	mock_cache.check = AsyncMock()
	mock_cache.set = AsyncMock()

	await mock_cache.check(short_url)
	await mock_cache.set(short_url, long_url)

	mock_cache.check.assert_awaited()
	mock_cache.set.assert_awaited()


	mock_db = mocker.patch("api.api.DataBase", autospec=True)

	mock_db.get_long_url = AsyncMock()

	await mock_db.get_long_url(short_url)

	mock_db.get_long_url.assert_awaited()


	response = client.get(f"/{short_url}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND
