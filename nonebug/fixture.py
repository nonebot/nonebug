import sys
from typing import Generator

import pytest

from nonebug.app import App, ProcessorApp
from nonebug.helpers import clear_module, clear_nonebot


@pytest.fixture
def nonebug_clear() -> Generator[None, None, None]:
    """
    Make a snapshot for sys.modules before initializing.
    Clear nonebot and other modules not in snapshot after test case running completed.
    Ensure every test case has a clean nonebot environment.

    By default, this fixture will be auto called by `nonebug_init`.
    """
    modules = tuple(sys.modules.keys())
    yield None
    clear_nonebot()
    for module in tuple(sys.modules.keys()):
        if module not in modules:
            clear_module(module)


@pytest.fixture
def nonebug_init(nonebug_clear: None, request) -> None:
    """
    Initialize nonebot before test case running.
    And clear nonebot after test case running completed.
    """
    # ensure nonebot is clean
    clear_nonebot()

    import nonebot

    nonebot.init(**getattr(request, "param", {}))


@pytest.fixture(name="app")
def nonebug_app(nonebug_init: None, monkeypatch: pytest.MonkeyPatch) -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    return App(monkeypatch)


@pytest.fixture
def processor_app(nonebug_init: None, monkeypatch: pytest.MonkeyPatch) -> ProcessorApp:
    """
    Call `nonebug_init` and return a new instance of Processor Test App.
    """
    return ProcessorApp(monkeypatch)


__all__ = ["nonebug_clear", "nonebug_init", "nonebug_app", "processor_app"]
