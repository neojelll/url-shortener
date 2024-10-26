from aiokafka import AIOKafkaProducer
from .logger import configure_logger
from loguru import logger
import os
import json


configure_logger()


class MessageBroker(object):
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=f"{os.environ["BROKER_HOST"]}:{os.environ["BROKER_PORT"]}",
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def send_data(self, data):
        logger.debug(f"Send data to message-broker... params: {repr(data)}")
        await self.producer.send_and_wait(
            os.environ["SHORTENER_TOPIC_NAME"], data.model_dump()
        )

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.producer.flush()
        await self.producer.stop()
