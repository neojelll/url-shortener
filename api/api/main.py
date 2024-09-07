from typing import Annotated, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from pydantic import BaseModel
import uvicorn
import asyncio
import uuid


fake_DB = {"prefix_osjkcso": "https://fastapi.tiangolo.com/tutorial/testing/#extended-testing-file"}


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
        #write to event bus
        await asyncio.sleep(1)
        return {"Task": str(task_num)}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="don`t correct url")


@app.get("/v1/url/shorten")
async def get_request():
    pass


@app.get("/{short_id}")
async def transport_to_long_url(short_id: str):
    long_url = fake_DB[short_id]
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)


uvicorn.run(app, host="127.0.0.1", port=8000)
