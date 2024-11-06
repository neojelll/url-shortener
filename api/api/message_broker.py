from aiokafka import AIOKafkaProducer
from .logger import configure_logger
from loguru import logger
import os
import json


configure_logger()


class MessageBroker:
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=f"{os.environ["BROKER_HOST"]}:{os.environ["BROKER_PORT"]}",
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def send_data(self, data: dict) -> None:
        try:
            logger.debug(f"Send data to broker, params: {repr(data)}")
            await self.producer.send_and_wait(os.environ["SHORTENER_TOPIC_NAME"], data)
            logger.debug(f"Successfully send data to broker: {data}")
        except Exception as e:
            logger.debug(f"Error when send data to broker: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.producer.flush()
        await self.producer.stop()
