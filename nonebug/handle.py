import asyncio
import os
from collections import defaultdict
from datetime import datetime
from nonebug import get_config
from nonebug.models import Bot, TestCase
from nonebug.typing import List, Dict, Type, Optional
from nonebug.exception import ApiDataAssertException, ApiOutOfBoundException, ApiActionAssertException
from nonebot import escape_tag
from nonebot.adapters import Event
from nonebot.exception import NoLogException, IgnoredException, StopPropagation
from nonebot.matcher import matchers as _matchers
from nonebot.rule import TrieRule
from nonebot.matcher import Matcher
from nonebot.message import _check_matcher, _event_postprocessors, _event_preprocessors
from nonebot.log import logger, default_filter, default_format
from nonebot.typing import T_Handler

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


async def handle_testcase(testcase: TestCase, log_output: bool = False,  log_name: Optional[str] = None, matchers: Optional[List[Type[Matcher]]] = None):
    log_dir = get_config().nonebug_log_dir
    log_name = log_name or testcase.name + \
        datetime.now().strftime(" %Y-%m-%d_%H_%M_%S")
    if not matchers:
        test_matchers = _matchers.copy()
    else:
        test_matchers = defaultdict(list)
        for matcher in matchers:
            test_matchers[matcher.priority].append(matcher)
    api_list = testcase.api_list
    count = 0
    if log_output:
        log_id = logger.add(os.path.join(log_dir, log_name + ".log"), filter=default_filter,
                        format=default_format, diagnose=False, encoding="utf-8")
        log_err_id = logger.add(os.path.join(log_dir, log_name + "_err.log"), level="ERROR",
                            filter=default_filter, format=default_format, encoding="utf-8")
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
        if api.mock:
            logger.opt(colors=True).info(
                f"<y>API <r>{api}</> is mocked, skip check</>")
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
            f"<y>API <r>{api}</> completed testing</>")
        return api.result.dict()

    testcase.bot.__class__._call_api = _call_api
    await handle_event(testcase.bot, testcase.event, test_matchers)
    logger.opt(colors=True).info(
        f"<ly><c>{testcase.name}</c> completed testing.</ly>")
    if log_output:
        logger.remove(log_id)
        logger.remove(log_err_id)
        f = open(os.path.join(log_dir, log_name + "_err.log"),"rb")
        if not f.read():
            f.close()
            os.remove(os.path.join(log_dir, log_name + "_err.log"))

    
async def handle_testcases(testcases: List[TestCase]):
    coros = list(map(lambda x: handle_testcase(x), testcases))
    if coros:
        for coro in coros:
            await asyncio.create_task(coro)
