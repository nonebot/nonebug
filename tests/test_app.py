import pytest

from nonebug import App


@pytest.mark.asyncio
async def test_app(app: App):
    with pytest.raises(RuntimeError, match="Another"):  # noqa: PT012
        async with app.test_api():
            async with app.test_api():
                ...
