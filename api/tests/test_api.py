from fastapi.testclient import TestClient
from fastapi import status
from api.api import app, is_valid_url
from unittest.mock import AsyncMock
import pytest_asyncio
import pytest

SHORT_URL = 'shortener.com'
LONG_URL = 'http://shortener.com/long'
EXPIRATION = 300
TASK_NUM = 'dwskdskodlap912u91i'


@pytest_asyncio.fixture
async def mock_producer(mocker):
    mock_broker = mocker.patch('api.api.BrokerProducer', autospec=True)
    mock_broker_instance = mock_broker.return_value
    mock_broker_instance.__aenter__.return_value = mock_broker_instance
    return mock_broker_instance


@pytest_asyncio.fixture
async def mock_consumer(mocker):
    mock_broker = mocker.patch('api.api.BrokerConsumer', autospec=True)
    mock_broker_instance = mock_broker.return_value
    mock_broker_instance.__aenter__.return_value = mock_broker_instance
    return mock_broker_instance


@pytest_asyncio.fixture
async def mock_cache(mocker):
    mock_cache = mocker.patch('api.api.Cache', autospec=True)
    mock_cache_instance = mock_cache.return_value
    mock_cache_instance.__aenter__.return_value = mock_cache_instance
    return mock_cache_instance


@pytest_asyncio.fixture
async def mock_db(mocker):
    mock_db = mocker.patch('api.api.DataBase', autospec=True)
    mock_db_instance = mock_db.return_value
    mock_db_instance.__aenter__.return_value = mock_db_instance
    return mock_db_instance


@pytest.fixture
def client():
    return TestClient(app)


def test_is_valid_url():
    assert is_valid_url('http://domain.ru/los')
    assert not is_valid_url('aldakooaj')
    assert not is_valid_url('')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'data, error, in_json',
    [
        ({'url': 'http://shortener.com/long'}, status.HTTP_200_OK, 'task'),
        (
            {'prefix': 'inbeer', 'expiration': 48},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'detail',
        ),
        (
            {'url': 'no valid url', 'prefix': 'inbeer', 'expiration': 48},
            status.HTTP_400_BAD_REQUEST,
            'detail',
        ),
    ],
)
async def test_post_correct_url(mock_producer, client, data, error, in_json):
    mock_broker_instance = mock_producer
    response = client.post('/v1/url/shorten', json=data)
    assert response.status_code == error
    assert in_json in response.json()
    await mock_broker_instance.send_data(data)
    mock_broker_instance.send_data.assert_awaited_with(data)


@pytest.mark.asyncio
async def test_get_short_url(mock_consumer, client):
    mock_broker_instance = mock_consumer
    response = client.get('v1/url/shorten?task_num=TASK_NUM')
    assert response.status_code == status.HTTP_200_OK
    await mock_broker_instance.consume_data(TASK_NUM)
    mock_broker_instance.consume_data.assert_awaited_with(TASK_NUM)


@pytest.mark.asyncio
async def test_get_short_url_exception(mock_consumer, client):
    mock_broker_instance = mock_consumer
    mock_broker_instance.consume_data = AsyncMock(return_value=None)
    response = client.get('v1/url/shorten?task_num=TASK_NUM')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    await mock_broker_instance.consume_data(TASK_NUM)
    mock_broker_instance.consume_data.assert_awaited_with(TASK_NUM)


@pytest.mark.asyncio
async def test_redirect_cache_hit(mock_cache, client):
    mock_cache_instance = mock_cache
    mock_cache_instance.check = AsyncMock(return_value=LONG_URL)
    response = client.get(f'/{SHORT_URL}', follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)


@pytest.mark.asyncio
async def test_redirect_cache_miss(mock_cache, mock_db, client):
    mock_cache_instance = mock_cache
    mock_cache_instance.check = AsyncMock(return_value=None)
    mock_cache_instance.set = AsyncMock()
    mock_db_instance = mock_db
    mock_db_instance.get_long_url = AsyncMock(return_value=LONG_URL)
    mock_db_instance.get_expiration = AsyncMock(return_value=EXPIRATION)
    response = client.get(f'/{SHORT_URL}', follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
    mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)
    mock_cache_instance.set.assert_awaited_once_with(SHORT_URL, LONG_URL, EXPIRATION)


@pytest.mark.asyncio
async def test_redirect_no_db_record(mock_cache, mock_db, client):
    mock_cache_instance = mock_cache
    mock_cache_instance.check = AsyncMock(return_value=None)
    mock_db_instance = mock_db
    mock_db_instance.get_long_url = AsyncMock(return_value=None)
    response = client.get(f'/{SHORT_URL}', follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.json()
    mock_cache_instance.check.assert_awaited_once_with(SHORT_URL)
    mock_db_instance.get_long_url.assert_awaited_once_with(SHORT_URL)
