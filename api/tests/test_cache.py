from unittest.mock import AsyncMock
from api.cache import Cache
import pytest


SHORT_URL = "shortener.com"
LONG_URL = "http://shortener.com/long"


@pytest.mark.asyncio
async def test_init(mocker):
	mock_cache = AsyncMock()

	mock_redis = mocker.patch("api.cache.Redis", autospec=True, return_value=mock_cache)

	Cache()

	mock_redis.assert_called_once_with(host='localhost', port=6379, db=0, decode_responses=True)

	
@pytest.mark.asyncio
async def test_aenter(mocker):
	mock_cache = AsyncMock()

	mocker.patch("api.cache.Redis", autospec=True, return_value=mock_cache)

	cache = Cache()
	
	async with cache as entered_cache:
		assert cache is entered_cache

	mock_cache.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_check_hit(mocker):
	mock_cache = AsyncMock()

	mocker.patch("api.cache.Redis", autospec=True, return_value=mock_cache)

	async with Cache() as cache:
		await cache.check(SHORT_URL)

	mock_cache.exists.assert_awaited_once_with(SHORT_URL)
	mock_cache.get.assert_awaited_once_with(SHORT_URL)
	mock_cache.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_check_miss(mocker):
	mock_cache = AsyncMock()

	mocker.patch("api.cache.Redis", autospec=True, return_value=mock_cache)

	mock_cache.exists = AsyncMock(return_value=False)

	async with Cache() as cache:
		assert await cache.check(SHORT_URL) is None

	mock_cache.exists.assert_awaited_once_with(SHORT_URL)
	mock_cache.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_set(mocker):
	mock_cache = AsyncMock()

	mocker.patch("api.cache.Redis", autospec=True, return_value=mock_cache)

	async with Cache() as cache:
		await cache.set(SHORT_URL, LONG_URL)

	mock_cache.set.assert_awaited_once_with(SHORT_URL, LONG_URL)
	mock_cache.close.assert_awaited_once_with()
