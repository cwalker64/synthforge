"""Small logging helper.

synthforge does not configure the root logger on import; applications keep
control of their own logging. Call :func:`get_logger` to obtain a namespaced
child logger, or :func:`enable_default_logging` for a quick console setup.
"""

from __future__ import annotations

import logging

_ROOT = "synthforge"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger under the ``synthforge`` namespace."""
    if name:
        return logging.getLogger(f"{_ROOT}.{name}")
    return logging.getLogger(_ROOT)


def enable_default_logging(level: int = logging.INFO) -> None:
    """Attach a simple ``StreamHandler`` to the package logger, once."""
    logger = get_logger()
    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
