from typing import Generator, AsyncGenerator

import pytest

from nonebug.app import App
from nonebug.helpers import clear_nonebot


@pytest.fixture
def nonebug_clear() -> Generator[None, None, None]:
    """
    Clear nonebot after test case running completed.
    Ensure every test case has a clean nonebot environment.

    By default, this fixture will be auto called by `nonebug_init`.
    """
    yield None
    clear_nonebot()


@pytest.fixture
def nonebug_init(nonebug_clear: None) -> None:
    """
    Initialize nonebot before test case running.
    And clear nonebot after test case running completed.
    """
    # ensure nonebot is clean
    clear_nonebot()

    import nonebot

    nonebot.init()


@pytest.fixture(name="app")
def nonebug_app(nonebug_init: None) -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    app = App()
    return app


__all__ = ["nonebug_clear", "nonebug_init", "nonebug_app"]
