from typing import Dict, List
from fastapi import FastAPI
from urllib.parse import urlparse
from jsonschema import validate
from json import load
import uvicorn
import asyncio
import uuid


app = FastAPI(
	title="URL Shortener API"
)


schema = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "prefix": {"type": "number"},
		"expiration": {"type": "number"}
    },
    "required": ["url"],
}


def is_valid_json(dct):
    try:
        validate(instance=dct, schema=schema)
        return True
    except:
        return False


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return bool(parsed_url.netloc)


@app.post("/v1/url/shorten")
async def post_url(url_json):
    url_dict = load(url_json)
    if is_valid_json(url_dict):
        url: str = url_dict.get("url")
        if is_valid_url(url):
            task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
            return {"Task": str(task_num)}
        return {"ERROR": "not valid url"}
    return {"ERROR": "dont write url"}


app.get("v1/url/shorten")
async def get_request():
    pass


uvicorn.run(app, host="127.0.0.1", port=8000)
