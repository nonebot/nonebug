import asyncio
from nonebug.models import Bot, TestCase
from nonebug.typing import List
from nonebug.exception import ApiDataAssertException, ApiOutOfBoundException, ApiActionAssertException
from nonebot.message import handle_event
from loguru import logger

async def handle_testcase_event(testcase: TestCase):
    api_list = testcase.api_list
    count = 0
    logger.info(f"Start test {testcase.name}")
    async def _call_api(bot: Bot, name: str, **kwargs) -> dict:
        logger.debug
        nonlocal count
        if count < len(api_list):
            api = api_list[count]
            count += 1
        else:
            raise ApiOutOfBoundException
        action = api.action
        if name != action:
            raise ApiActionAssertException(action, name)
        api_data = api.data.__dict__
        for k, v in kwargs.items():
            expert_v = api_data.get(k)
            if expert_v  == v:
                continue
            else:
                raise ApiDataAssertException(api.action, k, expert_v, v)
        return api.result.dict()
    testcase.bot.__class__._call_api = _call_api
    await handle_event(testcase.bot, testcase.event)
    logger.info(f"{testcase.name} tested success!")

async def handle_testcases(testcases: List[TestCase]):
    coros = list(map(lambda x : handle_testcase_event(x), testcases))
    if coros:
        for coro in coros:
            await asyncio.create_task(coro)