from loguru import logger
from api.api import app  # type: ignore
import uvicorn


def run():
    logger.info("Starting the server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
