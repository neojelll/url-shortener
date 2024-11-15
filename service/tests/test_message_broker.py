import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from service.message_broker import BrokerConsumer


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
        mock_consumer = AsyncMock()
        mocker.patch(
            'service.message_broker.AIOKafkaConsumer',
            return_value=mock_consumer,
        )
        return mock_consumer


@pytest.mark.asyncio
async def test_message_broker_init(mock_broker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'SHORTENER_TOPIC_NAME': 'my_topic',
        },
    ):
        _ = mock_broker
        broker = BrokerConsumer()
        assert broker.consumer is not None


@pytest.mark.asyncio
async def test_consume_data(mock_broker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'SHORTENER_TOPIC_NAME': 'my_topic',
        },
    ):
        mock_consumer = mock_broker
        mock_consumer.__aiter__.return_value = iter([AsyncMock(value=b'test_message')])

        async with BrokerConsumer() as broker:
            messages = [msg async for msg in broker.consume_data()]
            assert messages == ['test_message']


@pytest.mark.asyncio
async def test_consume_data_empty_message(mock_broker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'SHORTENER_TOPIC_NAME': 'my_topic',
        },
    ):
        mock_consumer = mock_broker
        mock_consumer.__aiter__.return_value = iter([AsyncMock(value=None)])

        async with BrokerConsumer() as broker:
            messages = [msg async for msg in broker.consume_data()]
            assert messages == []


@pytest.mark.asyncio
async def test_consume_data_error_handling(mock_broker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'SHORTENER_TOPIC_NAME': 'my_topic',
        },
    ):
        mock_consumer = mock_broker
        mock_consumer.__aiter__.side_effect = Exception('Test exception')

        async with BrokerConsumer() as broker:
            messages = [msg async for msg in broker.consume_data()]
            assert messages == []
