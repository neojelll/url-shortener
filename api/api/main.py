from loguru import logger
from .api import app #type: ignore


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
