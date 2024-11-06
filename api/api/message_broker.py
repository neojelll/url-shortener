from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .logger import configure_logger
from loguru import logger
import os
import json


configure_logger()


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
            await self.producer.send_and_wait(os.environ["SHORTENER_TOPIC_NAME"], data)
            logger.debug(f"Successfully send data to broker: {data}")
        except Exception as e:
            logger.debug(f"Error when send data to broker: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.producer.flush()
        await self.producer.stop()


class BrokerConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            os.environ["TASK_TOPIC_NAME"],
            bootstrap_servers=f"{os.environ['BROKER_HOST']}:{os.environ['BROKER_PORT']}",
            enable_auto_commit=False,
            group_id="group_2",
        )

    async def __aenter__(self):
        await self.consumer.start()
        return self

    async def consume_data(self, task_num: str) -> None | str:
        try:
            async for msg in self.consumer:
                logger.debug("start comsume data with task_topic")
                if msg.value is not None:
                    data: dict = json.loads(msg.value.decode("utf-8"))
                    if data["task"] == task_num:
                        short_url = data["short_url"]
                        await self.consumer.commit()
                        logger.debug(f"Completed consume data returned: {short_url}")
                        return short_url
                logger.warning("Received a message is None value")
        except Exception as e:
            logger.error(f"Error when consume data from kafka: {e}")

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.consumer.stop()
