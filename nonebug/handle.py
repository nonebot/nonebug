import asyncio
from collections import defaultdict
from nonebug.models  import TestCase
from nonebug.typing import List, Dict, Type, Optional
from nonebug.exception import ApiDataAssertException, ApiOutOfBoundException, ApiActionAssertException, ApiTypeAssertException
from nonebot import escape_tag
from nonebot.adapters import Event,Bot
from nonebot.exception import NoLogException, IgnoredException, StopPropagation
from nonebot.matcher import matchers as _matchers
from nonebot.rule import TrieRule
from nonebot.matcher import Matcher
from nonebot.message import _check_matcher, _event_postprocessors, _event_preprocessors
from nonebot.log import logger

async def handle_event(bot: "Bot", event: "Event", matchers: Dict[int, List[Type["Matcher"]]]):
    show_log = True
    log_msg = f"<m>{escape_tag(bot.type.upper())} {escape_tag(bot.self_id)}</m> | "
    try:
        log_msg += event.get_log_string()
    except NoLogException:
        show_log = False
    if show_log:
        logger.opt(colors=True).success(log_msg)

    state = {}
    coros = list(map(lambda x: x(bot, event, state), _event_preprocessors))
    if coros:
        try:
            if show_log:
                logger.debug("Running PreProcessors...")
            await asyncio.gather(*coros)
        except IgnoredException as e:
            logger.opt(colors=True).info(
                f"Event {escape_tag(event.get_event_name())} is <b>ignored</b>")
            return
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running EventPreProcessors. "
                "Event ignored!</bg #f8bbd0></r>")

    # Trie Match
    _, _ = TrieRule.get_value(bot, event, state)

    break_flag = False
    for priority in sorted(matchers.keys()):
        if break_flag:
            break

        if show_log:
            logger.debug(f"Checking for matchers in priority {priority}...")

        pending_tasks = [
            _check_matcher(priority, matcher, bot, event, state.copy())
            for matcher in matchers[priority]
        ]

        results = await asyncio.gather(*pending_tasks, return_exceptions=True)

        for result in results:
            if not isinstance(result, Exception):
                continue
            if isinstance(result, StopPropagation):
                break_flag = True
                logger.debug("Stop event propagation")
            else:
                logger.opt(colors=True, exception=result).error(
                    "<r><bg #f8bbd0>Error when checking Matcher.</bg #f8bbd0></r>"
                )

    coros = list(map(lambda x: x(bot, event, state), _event_postprocessors))
    if coros:
        try:
            if show_log:
                logger.debug("Running PostProcessors...")
            await asyncio.gather(*coros)
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running EventPostProcessors</bg #f8bbd0></r>"
            )


async def handle_testcase(testcase: TestCase, matchers: Optional[List[Type[Matcher]]] = None):
    if not matchers:
        test_matchers = _matchers.copy()
    else:
        test_matchers = defaultdict(list)
        for matcher in matchers:
            test_matchers[matcher.priority].append(matcher)
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
        logger.opt(colors=True).info(f"<y>API <r>{api}</> started testing</>")
        if api["mock"]:
            logger.opt(colors=True).info(
                f"<y>API <r>{api}</> is mocked, skip check</>")
            return api["result"]
        action = api["action"]
        assert action == name, ApiActionAssertException(action, name)
        api_data = api["data"]
        for k, v in kwargs.items():
            expect_v = api_data.get(k)
            #assert type(expect_v)==type(v), ApiTypeAssertException(action, k, type(expect_v), type(v))
            assert expect_v==v, ApiDataAssertException(action,k,expect_v,v)
        logger.opt(colors=True).info(
            f"<y>API <r>{api}</> completed testing</>")
        return api["result"]

    testcase.bot.__class__._call_api = _call_api
    await handle_event(testcase.bot, testcase.event, test_matchers)
    logger.opt(colors=True).info(
        f"<ly><c>{testcase.name}</c> completed testing.</ly>")

    
async def handle_testcases(testcases: List[TestCase]):
    coros = list(map(lambda x: handle_testcase(x), testcases))
    if coros:
        for coro in coros:
            await asyncio.create_task(coro)
