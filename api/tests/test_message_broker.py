from unittest.mock import AsyncMock
from api.message_broker import MessageBroker
import pytest


TOPIC = "test_topic"
DATA = {"url": "http://github.com/long"}


@pytest.mark.asyncio
async def test_init(mocker):
	mock_producer = AsyncMock()

	mocker.patch("api.message_broker.KafkaProducer", autospec=True,
			return_value=mock_producer)

	instance = MessageBroker()

	assert isinstance(instance, MessageBroker)


@pytest.mark.asyncio
async def test_aenter(mocker):
	mock_producer = AsyncMock()

	mocker.patch("api.message_broker.KafkaProducer", autospec=True, return_value=mock_producer)

	instance = MessageBroker()

	async with instance as entered_instance:
		assert instance is entered_instance

	mock_producer.flush.assert_awaited_once_with()
	mock_producer.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_send_data(mocker):
	mock_producer = AsyncMock()
    
	mocker.patch("api.message_broker.KafkaProducer", autospec=True, return_value=mock_producer)
    
	async with MessageBroker() as broker:
		await broker.send_data(TOPIC, DATA)

	mock_producer.send.assert_awaited_once_with(TOPIC, DATA)
	mock_producer.flush.assert_awaited_once_with()
	mock_producer.close.assert_awaited_once_with()
