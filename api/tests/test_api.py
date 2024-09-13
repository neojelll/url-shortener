from fastapi.testclient import TestClient
from fastapi import status

from api.api import app, is_valid_url
from api.adapter_to_message_broker import AdapterToMessageBroker
from api.message_broker import MessageBroker


client = TestClient(app)


def test_is_valid_url():
	assert is_valid_url("http://domain.ru/los")
	assert not is_valid_url("aldakooaj")
	assert not is_valid_url("")


def test_post_request(mocker):
	dct = {
		"url": "http://domain.ru/los/hex"
	}

	response = client.post("/v1/url/shorten", json=dct)
	assert response.status_code == status.HTTP_200_OK
	assert "task" in response.json()

	mock_broker = mocker.Mock(spec=MessageBroker)
	service = AdapterToMessageBroker(broker=mock_broker)
	service.process_data(dct)
	mock_broker.send_message.assert_called_once_with("data_queue", f"Processed: {dct}")


def test_post_request_error():
	response = client.post(
		"/v1/url/shorten", 
		json={
		"prefix": "inbeer", 
		"expiration": 48
		}
		)
	assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
	assert "detail" in response.json()


def test_get_request():
	response = client.get("/v1/url/shorten")
	assert response.status_code == status.HTTP_200_OK


def test_transport_to_long_url():
	response = client.get("/github.com}", follow_redirects=False)
	assert response.status_code == status.HTTP_302_FOUND
