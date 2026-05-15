"""Simple retry wrapper for brittle JSON / LLM outputs."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def with_retries(fn: Callable[[], T], *, attempts: int = 2, label: str = "llm") -> T:
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last = exc
            logger.warning("%s attempt %s failed: %s", label, i + 1, exc)
    assert last is not None
    raise last
