from service.cache import Cache, ttl
from unittest.mock import AsyncMock, patch
import pytest_asyncio
import pytest


SHORT_URL = 'shortener.com'
LONG_URL = 'http://url_shortener.com'
EXPIRATION = 5
TTL = '5000'


@pytest_asyncio.fixture
async def mock_cache(mocker):
    with patch.dict('os.environ', {'CACHE_HOST': 'redis', 'CACHE_PORT': '6379'}):
        mocker.patch('service.cache.min')
        mocker.patch('service.cache.ttl', autospec=True)
        mock_redis = mocker.patch('service.cache.Redis', autospec=True)
        mock_session = AsyncMock()
        mock_redis.return_value = mock_session
        cache = Cache()
        async with cache as cache_instance:
            yield cache_instance, mock_session


@pytest.mark.asyncio
async def test_ttl():
    with patch.dict('os.environ', {'CACHE_TTL': TTL}):
        result = await ttl()
        assert result == int(TTL)


@pytest.mark.asyncio
async def test_ttl_error(mocker):
    with patch.dict('os.environ', {'CACHE_TTL': 'invalid value'}):
        result = await ttl()
        assert result == 3600


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
    mock_session.set = AsyncMock(side_effect=Exception('Cache error'))
    await cache.create_recording(SHORT_URL, LONG_URL, EXPIRATION)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected, exists_return', [(False, False), (True, True)])
async def test_check_short_url(mock_cache, expected, exists_return):
    cache, mock_session = mock_cache
    mock_session.exists = AsyncMock(return_value=exists_return)
    result = await cache.check_short_url(SHORT_URL)
    assert result == expected
    mock_session.exists.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_short_url_error(mock_cache):
    cache, mock_session = mock_cache
    mock_session.exists.side_effect = Exception('Check Short_url error')
    result = await cache.check_short_url(SHORT_URL)
    assert not result
    mock_session.exists.assert_awaited_once()
