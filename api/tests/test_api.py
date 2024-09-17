from fastapi.testclient import TestClient
from fastapi import status

from api.api import app, is_valid_url

from unittest.mock import AsyncMock
import pytest


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
	mock_broker.send = AsyncMock()

	response = client.post("/v1/url/shorten", json=data)
	assert response.status_code == status.HTTP_200_OK
	assert "task" in response.json()

	await mock_broker.send("topic_name", data)
	mock_broker.send.assert_awaited()


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
	short_url = "github.com"
	long_url = "http://github.com/neojelll/shotener"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=long_url)

	response = client.get(f"/v1/url/shorten?short_url={short_url}")
	assert response.status_code == status.HTTP_200_OK
	assert "long_url" in response.json()

	await mock_cache_instance.check(short_url)
	mock_cache_instance.check.assert_awaited_with(short_url)


@pytest.mark.asyncio
async def test_get_cache_miss(mocker, client):
	short_url = "github.com"
	long_url = "http://github.com/neojelll/shotener"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__enter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=long_url)

	response = client.get(f"/v1/url/shorten?short_url={short_url}")
	assert response.status_code == status.HTTP_200_OK
	assert "long_url" in response.json()

	await mock_cache_instance.check(short_url)
	await mock_db_instance.get_long_url(short_url)
	mock_cache_instance.check.assert_awaited_with(short_url)
	mock_db_instance.get_long_url.assert_awaited_with(short_url)


@pytest.mark.asyncio
async def test_get_no_db_record(mocker, client):
	short_url = "github.com"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)  # Возвращаем None при вызове

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__enter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=None)

	response = client.get(f"/v1/url/shorten?short_url={short_url}")
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "detail" in response.json()

	await mock_cache_instance.check(short_url)
	await mock_db_instance.get_long_url(short_url)

	mock_cache_instance.check.assert_awaited_with(short_url)
	mock_db_instance.get_long_url.assert_awaited_with(short_url)


@pytest.mark.asyncio
async def test_redirect_cache_hit(mocker, client):
	short_url = "github.com"
	long_url = "http://github.com/neojelll/shotener"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=long_url)

	response = client.get(f"/{short_url}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND

	await mock_cache_instance.check(short_url)

	mock_cache_instance.check.assert_awaited_with(short_url)


@pytest.mark.asyncio
async def test_redirect_cache_miss(mocker, client):
	short_url = "github.com"
	long_url = "http://github.com/neojelll/shotener"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)
	mock_cache_instance.set = AsyncMock()

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__enter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=long_url)

	response = client.get(f"/{short_url}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND

	await mock_cache_instance.check(short_url)
	await mock_db_instance.get_long_url(short_url)
	await mock_cache_instance.set(short_url, long_url)

	mock_cache_instance.check.assert_awaited_with(short_url)
	mock_db_instance.get_long_url.assert_awaited_with(short_url)
	mock_cache_instance.set.assert_awaited_with(short_url, long_url)


@pytest.mark.asyncio
async def test_redirect_no_db_record(mocker, client):
	short_url = "github.com"

	mock_cache = mocker.patch("api.api.Cache", autospec=True)
	mock_cache_instance = mock_cache.return_value
	mock_cache_instance.__enter__.return_value = mock_cache_instance
	mock_cache_instance.check = AsyncMock(return_value=None)

	mock_db = mocker.patch("api.api.DataBase", autospec=True)
	mock_db_instance = mock_db.return_value
	mock_db_instance.__enter__.return_value = mock_db_instance
	mock_db_instance.get_long_url = AsyncMock(return_value=None)

	response = client.get(f"/{short_url}", follow_redirects=False)
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "detail" in response.json()

	await mock_cache_instance.check(short_url)
	await mock_db_instance.get_long_url(short_url)

	mock_cache_instance.check.assert_awaited_with(short_url)
	mock_db_instance.get_long_url.assert_awaited_with(short_url)
