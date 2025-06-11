from logging.handlers import RotatingFileHandler
from common.env import ENV_BACKEND_ROOT
import logging
import os

assert(ENV_BACKEND_ROOT)
LOGGER_DIR = ENV_BACKEND_ROOT + "/log"

LOG_FILE = "app.log"

os.makedirs(LOGGER_DIR, exist_ok=True)

log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

file_handler = RotatingFileHandler(
    os.path.join(LOGGER_DIR, LOG_FILE),
    maxBytes=1_000_000,  # 1MB
    backupCount=10       # 최대 10개 백업 보관
)
file_handler.setFormatter(log_formatter)

# 기본 로거 설정
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# 필요하면 콘솔도 같이 찍게 할 수 있음
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)