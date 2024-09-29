from unittest.mock import AsyncMock
from api.message_broker import MessageBroker
import pytest_asyncio
import pytest

TOPIC = "test_topic"
DATA = {"url": "http://github.com/long"}


@pytest_asyncio.fixture
async def mock_broker(mocker):
    mock_producer = AsyncMock()
    mocker.patch(
        "api.message_broker.KafkaProducer", autospec=True, return_value=mock_producer
    )
    broker = MessageBroker()
    async with broker as broker_instance:
        yield broker_instance, mock_producer


@pytest.mark.asyncio
async def test_init(mock_broker):
    broker, _ = mock_broker
    assert isinstance(broker, MessageBroker)


@pytest.mark.asyncio
async def test_aenter(mock_broker):
    broker, _ = mock_broker
    assert isinstance(broker, MessageBroker)


@pytest.mark.asyncio
async def test_send_data(mock_broker):
    broker, mock_producer = mock_broker
    await broker.send_data(TOPIC, DATA)
    mock_producer.send.assert_awaited_once_with(TOPIC, DATA)
