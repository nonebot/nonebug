import pytest
import pytest_asyncio

from nonebug.app import App

from . import NONEBOT_INIT_KWARGS, NONEBOT_START_LIFESPAN


@pytest_asyncio.fixture(scope="session", autouse=True)
async def nonebug_init(request: pytest.FixtureRequest):
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
    driver = nonebot.get_driver()
    if run_lifespan:
        try:
            await driver._lifespan.startup()
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error occurred while running startup hook."
                "</bg #f8bbd0></r>"
            )
            raise

    try:
        yield
    finally:
        if run_lifespan:
            try:
                await driver._lifespan.shutdown()
            except Exception as e:
                logger.opt(colors=True, exception=e).error(
                    "<r><bg #f8bbd0>Error occurred while running shutdown hook."
                    "</bg #f8bbd0></r>"
                )


@pytest.fixture(name="app")
def nonebug_app(nonebug_init) -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    return App()


__all__ = ["nonebug_init", "nonebug_app"]
