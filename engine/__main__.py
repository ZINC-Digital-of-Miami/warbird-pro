"""Launch the Warbird Pro Trading Command Center."""

import logging
import sys

import uvicorn

from engine.config import HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-20s %(levelname)-5s %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    uvicorn.run(
        "engine.server:app",
        host=HOST,
        port=PORT,
        log_level="info",
        ws_max_size=16 * 1024 * 1024,
    )
