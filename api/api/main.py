from loguru import logger
from .api import app
import uvicorn


def run() -> None:
    logger.debug("Start run")
    uvicorn.run(app, host="0.0.0.0", port=8000)
