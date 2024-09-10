from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from pydantic import BaseModel
from api.message_broker import MessageBroker
import uvicorn
import asyncio
import uuid


class MyService:
    def __init__(self, broker: MessageBroker):
        self.broker = broker

    def process_data(self, data):
        # Обработка данных и отправка сообщения
        message = f"Processed: {data}"
        self.broker.send_message("data_queue", message)


app = FastAPI(
	title="URL Shortener API"
)


class ShortURLRequest(BaseModel):
    url: str
    prefix: str = ""
    expiration: int = 24


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    print(parsed_url)
    return bool(parsed_url.netloc)


@app.post("/v1/url/shorten")
async def post_url(request: ShortURLRequest):
    url = request.url
    if is_valid_url(url):
        task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
        #отправка данных в кафку
        await asyncio.sleep(1)
        return {"task": str(task_num)}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid URL")


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/{short_id}")
async def transport_to_long_url(short_id: str):
    return RedirectResponse(url=f"http://{short_id}", status_code=status.HTTP_302_FOUND)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
