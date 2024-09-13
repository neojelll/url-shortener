from api import app, logger

if __name__ == "__main__":
    logger.info("Starting the server...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)