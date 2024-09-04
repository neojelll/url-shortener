from typing import Dict, List
from fastapi import FastAPI
from urllib.parse import urlparse
import uvicorn
import asyncio
import uuid

#создание приложения
app = FastAPI(
	title="URL Shortener API"
)

'''url_dict format
url_dict = {
    url: ...
    prefix: ...  | default = ""
    expiration: ... | default = 24 hours
    Task: Task-num
}'''
url_dict = {}

#проверка ссылки на коректность
def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return all([parsed_url.scheme, parsed_url.netloc])

#запрос из cURL or TelegramBot
@app.post("/v1/url/shorten")
async def post_url(url_dict: Dict[str, str]):
    url: str = url_dict.setdefault("url", "")
    if is_valid_url(url):
        task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
        url_dict.update({"Task": str(task_num)})
        return {"Task": str(task_num)}
    return {"ERROR": "not valid url"}

#запрос из кафки
app.get("v1/url/shorten")
async def get_request():
    pass


uvicorn.run(app, host="127.0.0.1", port=8000)
