from kafka import KafkaProducer
from loguru import logger
import json


class MessageBroker(object):
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

    async def __aenter__(self):
        return self

    async def send_data(self, topic: str, data):
        logger.debug(f"Send data to message-broker... params: {repr(data)}")
        await self.producer.send(topic, data)

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.producer.flush()  # type: ignore
        await self.producer.close()  # type: ignore
