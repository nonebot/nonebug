import pytest

from .app import App


@pytest.fixture
def processor_app(nonebug_init: None) -> App:
    """
    Call `nonebug_init` and return a new instance of Processor Test App.
    """
    return App()


__all__ = ["processor_app"]
