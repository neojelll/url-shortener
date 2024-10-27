from aiokafka import AIOKafkaConsumer
from .logger import configure_logger
from loguru import logger
import os


configure_logger()


class MessageBroker:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            os.environ["SHORTENER_TOPIC_NAME"],
            bootstrap_servers=f"{os.environ["BROKER_HOST"]}:{os.environ["BROKER_PORT"]}",
            group_id="group_1",
        )

    async def __aenter__(self):
        await self.consumer.start()
        return self

    async def consume_data(self):
        try:
            async for msg in self.consumer:
                logger.debug("start cycle")
                if msg.value is not None:
                    logger.debug(f"got data from kafka: {msg.value.decode('utf-8')}")
                    yield msg.value.decode("utf-8")
                logger.warning("Received a message is None value")
        except Exception as e:
            logger.error(f"Error when consume data from kafka: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.consumer.stop()
