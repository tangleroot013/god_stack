#!/usr/bin/env python3
import logging
import json
import os
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)

def setup_production_logging(log_dir="/var/log/god_stack"):
    logger = logging.getLogger("GodStack")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Stream Handler (Systemd Journal Visibility)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter(
        "\033[1;34m%(asctime)s\033[0m | \033[1;35m[%(levelname)s]\033[0m %(message)s",
        datefmt="%H:%M:%S"
    )
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # File Handler (Structured JSON Analytics Data)
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(f"{log_dir}/god_stack.json", encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    except PermissionError:
        pass

    return logger
