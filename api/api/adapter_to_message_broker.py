from api.message_broker import MessageBroker

class AdapterToMessageBroker:
    def __init__(self, broker: MessageBroker):
        self.broker = broker

    def process_data(self, data):
        # Обработка данных и отправка сообщения
        message = f"Processed: {data}"
        self.broker.send_message("data_queue", message)