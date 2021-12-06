from typing import Generator

import pytest

from nonebug.helpers import clear_nonebot


@pytest.fixture
def nonebug_clear() -> Generator[None, None, None]:
    yield None
    clear_nonebot()


@pytest.fixture
def nonebug_init(nonebug_clear: None) -> None:
    # ensure nonebot is clean
    clear_nonebot()

    import nonebot

    nonebot.init()


__all__ = ["nonebug_clear", "nonebug_init"]
