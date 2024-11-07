from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .logger import configure_logger
from loguru import logger
import json
import os


configure_logger()


class BrokerConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            os.environ["SHORTENER_TOPIC_NAME"],
            bootstrap_servers=f"{os.environ['BROKER_HOST']}:{os.environ['BROKER_PORT']}",
            group_id="group_1",
        )

    async def __aenter__(self):
        await self.consumer.start()
        return self

    async def consume_data(self):
        try:
            async for msg in self.consumer:
                logger.debug("start comsume data with kafka")
                if msg.value is not None:
                    logger.debug(f"got data from kafka: {msg.value.decode('utf-8')}")
                    yield msg.value.decode("utf-8")
                logger.warning("Received a message is None value")
        except Exception as e:
            logger.error(f"Error when consume data from kafka: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.consumer.stop()


class BrokerProducer:
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
            await self.producer.send_and_wait(os.environ["TASK_TOPIC_NAME"], data)
            logger.debug(f"Successfully send data to broker: {data}")
        except Exception as e:
            logger.debug(f"Error when send data to broker: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.producer.flush()
        await self.producer.stop()
