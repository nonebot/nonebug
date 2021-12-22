from typing import TYPE_CHECKING, Set

import pytest
from utils import load_plugin, make_fake_event

from nonebug import App
from nonebug.fixture import *

if TYPE_CHECKING:
    from nonebot.plugin import Plugin
    from nonebot.matcher import Matcher


@pytest.mark.asyncio
async def test_process(app: App, load_plugin: Set["Plugin"]):
    from tests.plugins.process import (
        test,
        test_pause,
        test_finish,
        test_reject,
        test_rule_permission_pass,
        test_rule_permission_not_pass,
    )

    async with app.test_matcher(test) as ctx:
        bot = ctx.create_bot()
        ctx.receive_event(bot, make_fake_event()())

    async with app.test_matcher(test_pause) as ctx:
        bot = ctx.create_bot()
        ctx.receive_event(bot, make_fake_event()())
        ctx.receive_event(bot, make_fake_event()())
        ctx.should_paused()

    async with app.test_matcher(test_reject) as ctx:
        bot = ctx.create_bot()
        ctx.receive_event(bot, make_fake_event()())
        ctx.receive_event(bot, make_fake_event()())
        ctx.should_rejected()

    async with app.test_matcher(test_finish) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event()()
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "message", "result")
        ctx.should_finished()

    async with app.test_matcher(test_finish) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event()()
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "message", "result")

    async with app.test_matcher(test_rule_permission_pass) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event()()
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()

    async with app.test_matcher(test_rule_permission_not_pass) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event()()
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()
        ctx.should_not_pass_permission()

    async with app.test_matcher(test_rule_permission_not_pass) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event()()
        ctx.receive_event(bot, event)
        ctx.should_ignore_rule()
        ctx.should_ignore_permission()
