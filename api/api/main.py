from typing import Annotated, Dict, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from jsonschema import validate
from pydantic import BaseModel
from json import load
import uvicorn
import asyncio
import uuid


app = FastAPI(
	title="URL Shortener API"
)


class Url(BaseModel):
    url: str

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
    print(parsed_url)
    return bool(parsed_url.netloc)


@app.post("/v1/url/shorten")
async def post_url(url: Annotated[str, Header()]):
    if is_valid_url(url):
        task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
        return {"Task": str(task_num)}
    raise HTTPException(status_code=400, detail="don`t correct url")


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/prefix-shorturl")
def transport_to_long_url(link: Annotated[str, Header()] = "https://fastapi.tiangolo.com/tutorial/testing/#extended-testing-file"):
    print(type(link))
    return RedirectResponse(url=link, status_code=302)


uvicorn.run(app, host="127.0.0.1", port=8000)
