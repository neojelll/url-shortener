from unittest.mock import AsyncMock
from api.message_broker import MessageBroker
import pytest

@pytest.mark.asyncio
async def test_init(mocker):
	mock_producer = AsyncMock()

	mocker.patch("api.message_broker.KafkaProducer", autospec=True,
			return_value=mock_producer)

	MessageBroker()


@pytest.mark.asyncio
async def test_aenter(mocker):
	mock_producer = AsyncMock()

	mock_producer.flush = AsyncMock(return_value=None)
	mock_producer.close = AsyncMock(return_value=None)
	
	mocker.patch("api.message_broker.KafkaProducer", return_value=mock_producer, autospec=True)

	broker = MessageBroker()

	async with broker as entered_broker:
		assert broker is entered_broker


@pytest.mark.asyncio
async def test_send_data(mocker):
	topic = "test_topic"
	data = {"url": "http://github.com/long"}

    # Create a mock producer instance
	mock_producer = AsyncMock()

	mock_producer.flush = AsyncMock(return_value=None)
	mock_producer.close = AsyncMock(return_value=None)
    
    # Patch the KafkaProducer to return our mock
	mocker.patch("api.message_broker.KafkaProducer", return_value=mock_producer)

    # Patch the logger
	mock_logger = mocker.patch("api.message_broker.logger", autospec=True)
    
	async with MessageBroker() as broker:
        # Call the send_data method
		await broker.send_data(topic, data)

    # Assert that the send method was called with the correct parameters
	mock_producer.send.assert_awaited_once_with(topic, data)

    # Verify the logger's debug method was called with the correct message
	mock_logger.debug.assert_called_with(f"Send data to message-broker... params: {repr(data)}")
