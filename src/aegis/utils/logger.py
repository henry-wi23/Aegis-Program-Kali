import logging
import os
import time
from datetime import datetime
from logging import LogRecord
from pathlib import Path
from typing import Any, Dict, Tuple

LOG_DIR = "logs"
LOG_LEVEL = logging.DEBUG
LOG_RETENTION_DAYS = 7

_LOGGER_METADATA: Dict[str, Tuple[str, str]] = {}
_ORIGINAL_RECORD_FACTORY = logging.getLogRecordFactory()
_STATE = {"record_factory_initialized": False}


def _ensure_record_factory_initialized() -> None:
    """Ensure the custom log record factory is installed exactly once."""

    if _STATE["record_factory_initialized"]:
        return

    def _log_record_factory(*args: Any, **kwargs: Any) -> LogRecord:
        record = _ORIGINAL_RECORD_FACTORY(*args, **kwargs)
        module_code, script_code = _LOGGER_METADATA.get(record.name, ("0000", "0000"))
        record.module_code = module_code
        record.script_code = script_code
        return record

    logging.setLogRecordFactory(_log_record_factory)
    _STATE["record_factory_initialized"] = True


class _DefaultErrorCodeFilter(logging.Filter):
    """Guarantee that all records carry an ``error_code`` attribute."""

    def filter(self, record: LogRecord) -> bool:  # noqa: D401 - short description
        if not hasattr(record, "error_code"):
            record.error_code = "--------"
        return True


def prune_old_logs(log_dir: str, max_age_days: int) -> None:
    """Delete log files in ``log_dir`` older than ``max_age_days`` days."""

    if max_age_days <= 0:
        return

    directory = Path(log_dir)
    if not directory.exists():
        return

    cutoff = time.time() - (max_age_days * 86400)
    for log_file in directory.glob("*.log"):
        try:
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
        except OSError:
            # If a file can't be removed, skip it. The logger setup should not fail.
            continue


def setup_logger(
    name: str,
    module_code: str = "0000",
    script_code: str = "0000",
    max_log_age_days: int = LOG_RETENTION_DAYS,
):
    """Configure and return a centralized logger.

    The logger writes to a fresh timestamped log file on every run and uses a
    console handler for immediate feedback. Log files older than ``max_log_age_days``
    are automatically pruned at startup.
    """

    _LOGGER_METADATA[name] = (module_code, script_code)
    _ensure_record_factory_initialized()

    prune_old_logs(LOG_DIR, max_log_age_days)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    timestamp = datetime.now().strftime("%d-%m-%Y--%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"aegis-run--{timestamp}.log")

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(module_code)s-%(script_code)s | %(error_code)s | "
        "%(name)-15s | %(message)s"
    )
    date_format = "%d/%m/%Y - %H:%M:%S"

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    console_handler.addFilter(_DefaultErrorCodeFilter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    file_handler.addFilter(_DefaultErrorCodeFilter())
    logger.addHandler(file_handler)

    return logger
