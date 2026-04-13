import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger() -> logging.Logger:
    log = logging.getLogger("app")
    if log.handlers:
        return log

    log.setLevel(logging.INFO)
    log.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    log.addHandler(stream)

    log_dir = Path(__file__).resolve().parents[2] / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=2_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        log.addHandler(file_handler)
    except OSError:
        logging.getLogger(__name__).warning(
            "Could not create log file at %s; using stdout only.",
            log_dir,
        )

    return log


setup_logger()

logger = logging.getLogger("app")
