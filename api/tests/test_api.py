from fastapi.testclient import TestClient
from fastapi import status

from api.api import app, is_valid_url

from unittest.mock import AsyncMock
import pytest


SHORT_URL = "shortener.com"
LONG_URL = "http://shortener.com/long"


@pytest.fixture
def client():
	return TestClient(app)


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los")
	assert not is_valid_url("aldakooaj")
	assert not is_valid_url("")


@pytest.mark.asyncio
async def test_post_correct_url(mocker, client):
	data = {
		"url": "http://domain.ru/los/hex"
	}

	mock_broker = mocker.patch('api.api.MessageBroker', autospec=True)
	mock_broker_instance = mock_broker.return_value
	mock_broker_instance.__aenter__.return_value = mock_broker_instance
	mock_broker_instance.send_data = AsyncMock()

	response = client.post("/v1/url/shorten", json=data)
	assert response.status_code == status.HTTP_200_OK
	assert "task" in response.json()

	await mock_broker_instance.send_data("topic_name", data)
	mock_broker_instance.send_data.assert_awaited_with("topic_name", data)


def test_post_no_url(client):
	response = client.post("/v1/url/shorten", json={"prefix": "inbeer", "expiration": 48})
	assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
	assert "detail" in response.json()


def test_post_dont_correct_url(client):
	response = client.post("/v1/url/shorten", json={"url": "no valid url", "prefix": "inbeer", "expiration": 48})
	assert response.status_code == status.HTTP_400_BAD_REQUEST
	assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_request_cache_hit(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=LONG_URL)

	response = client.get(f"/v1/url/shorten?short_url={SHORT_URL}")
	assert response.status_code == status.HTTP_200_OK
	assert "long_url" in response.json()

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)


@pytest.mark.asyncio
async def test_get_cache_miss(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)
	mock_cache_instance.set = AsyncMock()

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__aenter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=LONG_URL)

	response = client.get(f"/v1/url/shorten?short_url={SHORT_URL}")
	assert response.status_code == status.HTTP_200_OK
	assert "long_url" in response.json()

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
	mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)
	mock_cache_instance.set.assert_awaited_once_with(SHORT_URL, LONG_URL)


@pytest.mark.asyncio
async def test_get_no_db_record(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__aenter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=None)

	response = client.get(f"/v1/url/shorten?short_url={SHORT_URL}")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "detail" in response.json()

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
	mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)


@pytest.mark.asyncio
async def test_redirect_cache_hit(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=LONG_URL)

	response = client.get(f"/{SHORT_URL}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)


@pytest.mark.asyncio
async def test_redirect_cache_miss(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)
	mock_cache_instance.set = AsyncMock()

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__aenter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=LONG_URL)

	response = client.get(f"/{SHORT_URL}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
	mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)
	mock_cache_instance.set.assert_awaited_once_with(SHORT_URL, LONG_URL)


@pytest.mark.asyncio
async def test_redirect_no_db_record(mocker, client):
	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__aenter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__aenter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=None)

	response = client.get(f"/{SHORT_URL}", follow_redirects=False)
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "detail" in response.json()

	mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
	mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)
