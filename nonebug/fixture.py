from contextlib import asynccontextmanager, nullcontext

import pytest
from async_asgi_testclient import TestClient

from nonebug.app import App
from nonebug.mixin.driver import set_global_client

from . import NONEBOT_INIT_KWARGS, NONEBOT_START_LIFESPAN


@asynccontextmanager
async def lifespan_ctx():
    import nonebot
    from nonebot.drivers import ASGIMixin

    driver = nonebot.get_driver()

    if isinstance(driver, ASGIMixin):
        # if the driver has an asgi application
        # use asgi lifespan to startup/shutdown
        ctx = TestClient(driver.asgi)
        set_global_client(ctx)
    else:
        ctx = driver._lifespan

    try:
        await ctx.__aenter__()
    except Exception as e:
        logger.opt(colors=True, exception=e).error(
            "<r><bg #f8bbd0>Error occurred while running startup hook."
            "</bg #f8bbd0></r>"
        )
        raise

    try:
        yield
    finally:
        try:
            await ctx.__aexit__(None, None, None)
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error occurred while running shutdown hook."
                "</bg #f8bbd0></r>"
            )


@pytest.fixture(scope="session", autouse=True)
async def nonebug_init(request: pytest.FixtureRequest):  # noqa: PT004
    """
    Initialize nonebot before test case running.
    """
    import nonebot
    from nonebot import logger
    from nonebot.matcher import matchers

    from nonebug.provider import NoneBugProvider

    nonebot.init(**request.config.stash.get(NONEBOT_INIT_KWARGS, {}))
    matchers.set_provider(NoneBugProvider)

    run_lifespan = request.config.stash.get(NONEBOT_START_LIFESPAN, True)

    ctx = lifespan_ctx() if run_lifespan else nullcontext()

    async with ctx:
        yield


@pytest.fixture(name="app")
def nonebug_app(nonebug_init) -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    return App()


__all__ = ["nonebug_init", "nonebug_app"]
