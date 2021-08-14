import asyncio
from nonebug.models import Bot, TestCase
from nonebug.typing import List
from nonebug.exception import ApiDataAssertException, ApiOutOfBoundException, ApiActionAssertException
from nonebot.message import handle_event
from loguru import logger


async def handle_testcase(testcase: TestCase):
    api_list = testcase.api_list
    count = 0
    logger.opt(colors=True).info(
        f"<ly><c>{testcase.name}</c> started testing.</ly>")

    async def _call_api(bot: Bot, name: str, **kwargs) -> dict:
        nonlocal count
        if count < len(api_list):
            api = api_list[count]
            count += 1
        else:
            raise ApiOutOfBoundException
        logger.opt(colors=True).info(f"<y>API <g>{api}</> started testing</>")
        if api.mock:
            logger.opt(colors=True).info(
                f"<y>API <g>{api}</> is mocked, skip check</>")
            return api.result.dict()
        action = api.action
        if name != action:
            raise ApiActionAssertException(action, name)
        api_data = api.data.dict()
        for k, v in kwargs.items():
            expect_v = api_data.get(k)
            if expect_v == v:
                continue
            else:
                raise ApiDataAssertException(api.action, k, expect_v, v)
        logger.opt(colors=True).info(
            f"<y>API <g>{api}</> completed testing</>")
        return api.result.dict()
    testcase.bot.__class__._call_api = _call_api
    await handle_event(testcase.bot, testcase.event)
    logger.opt(colors=True).info(
        f"<ly><c>{testcase.name}</c> completed testing.</ly>")


async def handle_testcases(testcases: List[TestCase]):
    coros = list(map(lambda x: handle_testcase(x), testcases))
    if coros:
        for coro in coros:
            await asyncio.create_task(coro)
