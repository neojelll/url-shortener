from api.message_broker import BrokerProducer, BrokerConsumer
from unittest.mock import AsyncMock, patch
from api.api import ShortURLRequest
import pytest_asyncio
import pytest
import asyncio
import json


DATA = ShortURLRequest(url='http://shortener.com', prefix='short', expiration=24)
TASK_NUM = '1232jdskoiw92'
SHORT_URL = 'short.com'


@pytest_asyncio.fixture
async def mock_producer(mocker):
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
async def test_init(mock_producer):
    broker, _ = mock_producer
    assert isinstance(broker, BrokerProducer)


@pytest.mark.asyncio
async def test_aenter(mock_producer):
    broker, _ = mock_producer
    assert isinstance(broker, BrokerProducer)


@pytest.mark.asyncio
async def test_send_data(mock_producer):
    broker, mock_producer = mock_producer
    await broker.send_data(DATA)
    mock_producer.send_and_wait.assert_awaited_once_with('my_topic', DATA)


@pytest.mark.asyncio
async def test_send_data_error(mock_producer):
    broker, mock_producer = mock_producer
    mock_producer.send_and_wait.side_effect = Exception('Broker Error')
    result = await broker.send_data(DATA)
    assert result is None
    mock_producer.send_and_wait.assert_awaited_once_with('my_topic', DATA)


@pytest_asyncio.fixture
async def mock_consumer(mocker):
    with patch.dict(
        'os.environ',
        {
            'BROKER_HOST': 'kafka',
            'BROKER_PORT': '9092',
            'TASK_TOPIC_NAME': 'my_topic2',
        },
    ):
        mock_consumer = AsyncMock()
        mocker.patch(
            'api.message_broker.AIOKafkaConsumer',
            autospec=True,
            return_value=mock_consumer,
        )
        consumer = BrokerConsumer()

        async with consumer as consumer_instance:
            yield consumer_instance, mock_consumer


@pytest.mark.asyncio
async def test_consumer_init(mock_consumer):
    consumer, _ = mock_consumer
    assert isinstance(consumer, BrokerConsumer)


@pytest.mark.asyncio
async def test_consume_data_success(mock_consumer):
    consumer, mock_consumer = mock_consumer

    msg = {'task': TASK_NUM, 'short_url': SHORT_URL}

    mock_consumer.__anext__.return_value = AsyncMock(
        value=json.dumps(msg).encode('utf-8')
    )
    mock_consumer.commit = AsyncMock()

    result = await consumer.consume_data(TASK_NUM)

    assert result == SHORT_URL
    mock_consumer.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_consume_data_no_matching_task(mock_consumer):
    consumer, mock_consumer = mock_consumer

    msg = {'task': 'task_2', 'short_url': SHORT_URL}

    mock_consumer.__anext__.return_value = AsyncMock(
        value=json.dumps(msg).encode('utf-8')
    )
    mock_consumer.commit = AsyncMock()

    result = await consumer.consume_data(TASK_NUM)

    assert result is None
    mock_consumer.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_consume_data_timeout(mock_consumer):
    consumer, mock_consumer = mock_consumer

    mock_consumer.__anext__.side_effect = asyncio.TimeoutError()

    result = await consumer.consume_data(TASK_NUM)

    assert result is None


@pytest.mark.asyncio
async def test_consume_data_none_value(mock_consumer):
    consumer, mock_consumer = mock_consumer

    mock_consumer.__anext__.return_value = AsyncMock(value=None)

    result = await consumer.consume_data(TASK_NUM)

    assert result is None


@pytest.mark.asyncio
async def test_consume_data_exception(mock_consumer):
    consumer, mock_consumer = mock_consumer

    mock_consumer.__anext__.side_effect = Exception('Simulated error')

    result = await consumer.consume_data(TASK_NUM)

    assert result is None
