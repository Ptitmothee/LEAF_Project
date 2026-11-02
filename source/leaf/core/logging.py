"""Structured logging with automated secret sanitization for LEAF."""

import logging
import re
import sys
from pathlib import Path

# Regular expressions and replacements matching common API keys, tokens, and authorization credentials
_SECRET_PATTERNS = [
    (re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{12,}", re.IGNORECASE), r"\1***REDACTED***"),
    (
        re.compile(
            r"(api[_\-]?key\s*[:=]\s*['\"]?)[A-Za-z0-9_\-\.]{12,}(['\"]?)", re.IGNORECASE
        ),
        r"\1***REDACTED***\2",
    ),
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}", re.IGNORECASE), r"sk-***REDACTED***"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{30,40}", re.IGNORECASE), r"AIza***REDACTED***"),
    (
        re.compile(r"(secret\s*[:=]\s*['\"]?)[A-Za-z0-9_\-\.]{12,}(['\"]?)", re.IGNORECASE),
        r"\1***REDACTED***\2",
    ),
]


class SecretSanitizingFormatter(logging.Formatter):
    """Logging formatter that automatically masks API keys and sensitive tokens."""

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for pattern, replacement in _SECRET_PATTERNS:
            formatted = pattern.sub(replacement, formatted)
        return formatted


_LOGGER_INITIALIZED = False


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    """Configure the root 'leaf' logger with structured formatting and secret sanitization.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to write log output.

    Returns:
        Configured root logger for the 'leaf' namespace.
    """
    global _LOGGER_INITIALIZED

    logger = logging.getLogger("leaf")
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not _LOGGER_INITIALIZED:
        logger.handlers.clear()

        # Console handler (standard stderr)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)
        format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        formatter = SecretSanitizingFormatter(fmt=format_str, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.propagate = False
        _LOGGER_INITIALIZED = True

    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtain a child logger under the 'leaf' hierarchy."""
    if not _LOGGER_INITIALIZED:
        setup_logging()
    if name.startswith("leaf"):
        return logging.getLogger(name)
    return logging.getLogger(f"leaf.{name}")
