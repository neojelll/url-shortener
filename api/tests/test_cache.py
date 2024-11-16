from unittest.mock import AsyncMock, patch
from api.cache import Cache, ttl
import pytest_asyncio
import pytest


TTL = '5000'
EXPIRATION = 500
SHORT_URL = 'http://shortener.com'
LONG_URL = 'http://shortener.com/longurl'


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


@pytest_asyncio.fixture
async def mock_cache(mocker):
    with patch.dict('os.environ', {'CACHE_HOST': 'redis', 'CACHE_PORT': '6379'}):
        mock_session = AsyncMock()
        mocker.patch('api.cache.Redis', autospec=True, return_value=mock_session)
        cache = Cache()
        async with cache as instance_cache:
            yield mock_session, instance_cache


@pytest.mark.asyncio
async def test_init(mock_cache):
    cache = Cache()
    assert isinstance(cache, Cache)


@pytest.mark.asyncio
async def test_aenter(mock_cache):
    async with Cache() as cache_instance:
        assert isinstance(cache_instance, Cache)


@pytest.mark.asyncio
async def test_check(mock_cache):
    mock_session, cache = mock_cache
    mock_session.get.return_value = LONG_URL
    result = await cache.check(SHORT_URL)
    assert result == LONG_URL


@pytest.mark.asyncio
async def test_check_error(mock_cache):
    mock_session, cache = mock_cache
    mock_session.get.side_effect = Exception('Cache Error')
    result = await cache.check(SHORT_URL)
    assert result is None


@pytest.mark.asyncio
async def test_set(mock_cache):
    mock_session, cache = mock_cache
    mock_session.set = AsyncMock()
    await cache.set(SHORT_URL, LONG_URL, EXPIRATION)
    mock_session.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_set_error(mock_cache):
    mock_session, cache = mock_cache
    mock_session.set = AsyncMock(side_effect=Exception('set error'))
    await cache.set(SHORT_URL, LONG_URL, EXPIRATION)
    mock_session.set.assert_awaited_once()
