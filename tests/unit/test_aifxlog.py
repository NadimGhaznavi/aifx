# tests/unit/test_aifxlog.py
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

import logging

import pytest

from aifx.constants.DLogging import DAiFxLog, LOG_LEVELS
from aifx.constants.DModule import DModule as MODULE
from aifx.utils.AiFxLog import AiFxLog


def _cleanup_logger(client_id: str) -> None:
    logger = logging.getLogger(client_id)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.propagate = True


@pytest.fixture
def clean_logger():
    client_ids: list[str] = []

    def register(client_id: str) -> str:
        _cleanup_logger(client_id)
        client_ids.append(client_id)
        return client_id

    yield register

    for client_id in client_ids:
        _cleanup_logger(client_id)


def test_aifxlog_uses_module_name_as_logger_client_id(clean_logger) -> None:
    client_id = clean_logger(MODULE.DB_MGR)

    log = AiFxLog(client_id=client_id, to_console=False)

    assert log._logger.name == MODULE.DB_MGR


def test_aifxlog_sets_configured_log_level(clean_logger) -> None:
    client_id = clean_logger(f"{MODULE.DB_MGR}.level")

    log = AiFxLog(
        client_id=client_id,
        to_console=False,
        log_level=DAiFxLog.WARNING,
    )

    assert log._logger.level == LOG_LEVELS[DAiFxLog.WARNING]


def test_aifxlog_adds_one_console_handler(clean_logger) -> None:
    client_id = clean_logger(f"{MODULE.BROKER}.console")

    log = AiFxLog(client_id=client_id, to_console=True)

    console_handlers = [
        handler
        for handler in log._logger.handlers
        if isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
    ]
    assert len(console_handlers) == 1


def test_aifxlog_does_not_duplicate_console_handlers(clean_logger) -> None:
    client_id = clean_logger(f"{MODULE.BROKER}.console_duplicate")

    first = AiFxLog(client_id=client_id, to_console=True)
    second = AiFxLog(client_id=client_id, to_console=True)

    console_handlers = [
        handler
        for handler in second._logger.handlers
        if isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
    ]
    assert first._logger is second._logger
    assert len(console_handlers) == 1


def test_aifxlog_adds_one_file_handler(clean_logger, tmp_path) -> None:
    client_id = clean_logger(f"{MODULE.OANDA_MGR}.file")
    log_file = str(tmp_path / "aifx.log")

    log = AiFxLog(client_id=client_id, log_file=log_file, to_console=False)

    file_handlers = [
        handler
        for handler in log._logger.handlers
        if isinstance(handler, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename == log_file


def test_aifxlog_does_not_duplicate_file_handlers(clean_logger, tmp_path) -> None:
    client_id = clean_logger(f"{MODULE.OANDA_MGR}.file_duplicate")
    log_file = str(tmp_path / "aifx.log")

    first = AiFxLog(client_id=client_id, log_file=log_file, to_console=False)
    second = AiFxLog(client_id=client_id, log_file=log_file, to_console=False)

    file_handlers = [
        handler
        for handler in second._logger.handlers
        if isinstance(handler, logging.FileHandler)
    ]
    assert first._logger is second._logger
    assert len(file_handlers) == 1


def test_loglevel_changes_logger_level(clean_logger) -> None:
    client_id = clean_logger(f"{MODULE.SERVER_MQ}.loglevel")
    log = AiFxLog(client_id=client_id, to_console=False, log_level=DAiFxLog.INFO)

    log.loglevel(DAiFxLog.ERROR)

    assert log._logger.level == LOG_LEVELS[DAiFxLog.ERROR]


def test_invalid_log_level_raises_key_error(clean_logger) -> None:
    client_id = clean_logger(f"{MODULE.SERVER_MQ}.invalid")

    with pytest.raises(KeyError):
        AiFxLog(client_id=client_id, to_console=False, log_level="bogus")


def test_logging_methods_accept_normal_messages(clean_logger, tmp_path) -> None:
    client_id = clean_logger(f"{MODULE.CLIENT_QT}.methods")
    log_file = str(tmp_path / "aifx.log")
    log = AiFxLog(
        client_id=client_id,
        log_file=log_file,
        to_console=False,
        log_level=DAiFxLog.DEBUG,
    )

    log.debug("debug message")
    log.info("info message")
    log.warning("warning message")
    log.error("error message")
    log.critical("critical message")

    for handler in log._logger.handlers:
        handler.flush()

    text = (tmp_path / "aifx.log").read_text()
    assert "debug message" in text
    assert "info message" in text
    assert "warning message" in text
    assert "error message" in text
    assert "critical message" in text
