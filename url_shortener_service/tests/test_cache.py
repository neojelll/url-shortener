from url_shortener_service.cache import Cache, ttl
from unittest.mock import AsyncMock
import pytest_asyncio
import pytest


SHORT_URL = "shortener.com"
LONG_URL = "http://url_shortener.com"
EXPIRATION = 5


@pytest_asyncio.fixture
async def mock_cache(mocker):
    mocker.patch("url_shortener_service.cache.min")
    mocker.patch("url_shortener_service.cache.ttl", autospec=True)
    mock_redis = mocker.patch("url_shortener_service.cache.Redis", autospec=True)
    mock_session = AsyncMock()
    mock_redis.return_value = mock_session
    cache = Cache()
    async with cache as cache_instance:
        yield cache_instance, mock_session


def test_ttl(mocker):
    mocker.patch("url_shortener_service.cache.os", autospec=True)
    ttl()


@pytest.mark.asyncio
async def test_init(mock_cache):
    cache, _ = mock_cache
    assert isinstance(cache, Cache)


@pytest.mark.asyncio
async def test_aenter(mock_cache):
    cache, _ = mock_cache
    assert isinstance(cache, Cache)


@pytest.mark.asyncio
async def test_create_recording(mock_cache):
    cache, mock_session = mock_cache
    mock_session.set = AsyncMock()
    await cache.create_recording(SHORT_URL, LONG_URL, EXPIRATION)
    mock_session.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_recording_error(mock_cache):
    cache, mock_session = mock_cache
    mock_session.set = AsyncMock(side_effect=Exception("Cache error"))
    await cache.create_recording(SHORT_URL, LONG_URL, EXPIRATION)
