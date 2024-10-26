from aiokafka import AIOKafkaProducer
from .logger import configure_logger
from loguru import logger
import json


configure_logger()


class MessageBroker(object):
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def send_data(self, topic: str, data):
        logger.debug(f"Send data to message-broker... params: {repr(data)}")
        await self.producer.send_and_wait(topic, data)

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.producer.flush()
        await self.producer.stop()
