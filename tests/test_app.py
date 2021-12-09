import pytest

from nonebug import App
from nonebug.fixture import *


@pytest.mark.asyncio
async def test_app(app: App):
    try:
        async with app.test_api():
            async with app.test_api():
                ...
    except RuntimeError as e:
        assert "Another" in e.args[0]
    else:
        assert False, "App context cannot be nested"
