import logging
import sys
from pathlib import Path

logger = logging.getLogger()

formatter = logging.Formatter(fmt="%(levelname)s: [%(asctime)s] - %(module)s:%(lineno)d - %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(Path("src", "app.log"))

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

logger.setLevel(logging.INFO)


