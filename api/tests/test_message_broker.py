from api.message_broker import BrokerProducer
from unittest.mock import AsyncMock, patch
from api.api import ShortURLRequest
import pytest_asyncio
import pytest


DATA = ShortURLRequest(url='http://shortener.com', prefix='short', expiration=24)


@pytest_asyncio.fixture
async def mock_broker(mocker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'SHORTENER_TOPIC_NAME': 'my_topic',
        },
    ):
        mock_producer = AsyncMock()
        mocker.patch(
            'api.message_broker.AIOKafkaProducer',
            autospec=True,
            return_value=mock_producer,
        )
        broker = BrokerProducer()
        async with broker as broker_instance:
            yield broker_instance, mock_producer


@pytest.mark.asyncio
async def test_init(mock_broker):
    broker, _ = mock_broker
    assert isinstance(broker, BrokerProducer)


@pytest.mark.asyncio
async def test_aenter(mock_broker):
    broker, _ = mock_broker
    assert isinstance(broker, BrokerProducer)


@pytest.mark.asyncio
async def test_send_data(mock_broker):
    broker, mock_producer = mock_broker
    await broker.send_data(DATA)
    mock_producer.send_and_wait.assert_awaited_once_with('my_topic', DATA)


@pytest.mark.asyncio
async def test_send_data_error(mock_broker):
    broker, mock_producer = mock_broker
    mock_producer.send_and_wait.side_effect = Exception('Broker Error')
    result = await broker.send_data(DATA)
    assert result is None
    mock_producer.send_and_wait.assert_awaited_once_with('my_topic', DATA)
