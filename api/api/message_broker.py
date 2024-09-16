from kafka import KafkaProducer
from loguru import logger
import json


class MessageBroker(object):
	def __init__(self):
		self.producer = KafkaProducer(
			bootstrap_servers="localhost:9092",
			value_serializer=lambda x: json.dumps(x).encode("utf-8")
		)
		
	def __enter__(self):
		return self

	def send_data(self, topic: str, data):
		logger.debug(f"Send data to message-broker... params: {repr(data)}")
		self.producer.send(topic, data)

	def __exit__(self, exc_type, exc_value, traceback):
		self.producer.flush()
		self.producer.close()
