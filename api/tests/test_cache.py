from unittest.mock import AsyncMock
from api.cache import Cache
import pytest_asyncio
import pytest

SHORT_URL = "shortener.com"
LONG_URL = "http://shortener.com/long"
EXPIRATION = 300


@pytest_asyncio.fixture
async def mock_cache(mocker):
    mock_c = AsyncMock()
    mocker.patch("api.cache.Redis", autospec=True, return_value=mock_c)
    cache = Cache()
    async with cache as instance_cache:
        yield instance_cache, mock_c


@pytest.fixture
def mock_ttl(mocker):
    mocker.patch("api.cache.ttl", autospec=True, return_value=EXPIRATION)
    return 1000


def setup_get_result(mock_cache, return_value):
    mock_cache.get.return_value = return_value


@pytest.mark.asyncio
async def test_init(mock_cache):
    cache, _ = mock_cache
    assert isinstance(cache, Cache)


@pytest.mark.asyncio
async def test_aenter(mock_cache):
    cache, _ = mock_cache
    assert isinstance(cache, Cache)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "short_url, get_return, expected",
    [
        (SHORT_URL, LONG_URL, LONG_URL),
        ("non_existent_short_url", None, None),
    ],
)
async def test_check(mock_cache, short_url, get_return, expected):
    cache, mock_c = mock_cache
    setup_get_result(mock_c, get_return)
    result = await cache.check(short_url)
    assert result == expected
    mock_c.get.assert_awaited_once_with(short_url)


@pytest.mark.asyncio
async def test_set(mock_cache, mock_ttl):
    cache, mock_c = mock_cache
    await cache.set(SHORT_URL, LONG_URL, EXPIRATION)
    mock_c.set.assert_awaited_once_with(
        SHORT_URL, LONG_URL, ex=min(EXPIRATION, mock_ttl)
    )
