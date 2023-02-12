import pytest

from nonebug import App


@pytest.mark.asyncio
async def test_app(app: App):
    with pytest.raises(RuntimeError, match="Another"):
        async with app.test_api():
            async with app.test_api():
                ...
