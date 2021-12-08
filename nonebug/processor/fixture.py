from typing import AsyncGenerator

import pytest

from .app import App


@pytest.fixture
def processor_app(nonebug_init: None) -> App:
    """
    Call `nonebug_init` and return a new instance of Processor Test App.
    """
    app = App()
    return app


__all__ = ["processor_app"]
