from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
import uvicorn
import asyncio


app = FastAPI()


@app.get('/')
async def main() -> Dict[str, str]:
	return {"name": "surname"}


@app.post('/')
async def sum(num1: int = 10, num2: int = 5) -> Dict[str, int]:
	return {"sum": num1 + num2}


uvicorn.run(app, host="127.0.0.1", port=8000)