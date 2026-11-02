"""Unit tests for structured logging and secret sanitization."""

import logging

from leaf.core.logging import SecretSanitizingFormatter, get_logger


def test_secret_sanitizing_formatter_masks_keys():
    """Verify that credentials and API tokens are redacted by the formatter."""
    formatter = SecretSanitizingFormatter(fmt="%(message)s")

    test_cases = [
        ("Calling OpenAI with sk-1234567890abcdef1234567890 now", "sk-***REDACTED***"),
        ("Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "Bearer ***REDACTED***"),
        ("Google API Key: AIzaSyD9494kfkdks9494kfks9494kfks9494k", "AIza***REDACTED***"),
        ("Config secret='super_secret_token_12345'", "secret='***REDACTED***'"),
    ]

    for raw_msg, expected_in_result in test_cases:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg=raw_msg,
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert expected_in_result in formatted
        # Ensure the sensitive raw secret is NOT leaked
        if "sk-" in raw_msg:
            assert "sk-1234567890abcdef1234567890" not in formatted
        if "AIza" in raw_msg:
            assert "AIzaSyD9494kfkdks9494kfks9494kfks9494k" not in formatted


def test_logger_hierarchy():
    """Verify that get_logger produces loggers within the leaf namespace."""
    logger = get_logger("runner.sandbox")
    assert logger.name == "leaf.runner.sandbox"
