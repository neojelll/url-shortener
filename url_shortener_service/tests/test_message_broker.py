import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from url_shortener_service.message_broker import MessageBroker


@pytest_asyncio.fixture
async def mock_broker(mocker):
    mock_consumer = AsyncMock()

    mocker.patch(
        "url_shortener_service.message_broker.AIOKafkaConsumer",
        return_value=mock_consumer,
    )

    return mock_consumer


@pytest.mark.asyncio
async def test_message_broker_init(mock_broker):
    _ = mock_broker
    broker = MessageBroker()
    assert broker.consumer is not None


@pytest.mark.asyncio
async def test_consume_data(mock_broker):
    mock_consumer = mock_broker
    mock_consumer.__aiter__.return_value = iter([AsyncMock(value=b"test_message")])

    async with MessageBroker() as broker:
        messages = [msg async for msg in broker.consume_data()]
        assert messages == ["test_message"]


@pytest.mark.asyncio
async def test_consume_data_empty_message(mock_broker):
    mock_consumer = mock_broker
    mock_consumer.__aiter__.return_value = iter([AsyncMock(value=None)])

    async with MessageBroker() as broker:
        messages = [msg async for msg in broker.consume_data()]
        assert messages == []


@pytest.mark.asyncio
async def test_consume_data_error_handling(mock_broker):
    mock_consumer = mock_broker
    mock_consumer.__aiter__.side_effect = Exception("Test exception")

    async with MessageBroker() as broker:
        messages = [msg async for msg in broker.consume_data()]
        assert messages == []
