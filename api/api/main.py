from typing import Dict, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import RedirectResponse
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
    print(parsed_url)
    return bool(parsed_url.netloc)


@app.post("/v1/url/shorten")
async def post_url(url_dict = Header()):
    if is_valid_json(url_dict):
        url: str = url_dict.get("url")
        if is_valid_url(url):
            task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(url).netloc)
            return {"Task": str(task_num)}
        raise HTTPException(status_code=400, detail="don`t correct url")
    raise HTTPException(status_code=400, detail="you didn`t enter a url")


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/prefix-shorturl")
def transport_to_long_url(url_dict = Header()):
    return RedirectResponse(url=url_dict.get("url"), status_code=302)


uvicorn.run(app, host="127.0.0.1", port=8000)
