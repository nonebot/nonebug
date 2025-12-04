import pytest

from nonebug import App
from tests.utils import make_fake_event, make_fake_message


@pytest.mark.asyncio
async def test_process(app: App):
    from tests.plugins.process import (
        test,
        test_ignore,
        test_not_pass_perm,
        test_not_pass_rule,
    )

    Message = make_fake_message()

    async with app.test_matcher() as ctx:
        adapter = ctx.create_adapter()
        bot = ctx.create_bot(adapter=adapter)

        event = make_fake_event(_message=Message())()
        ctx.receive_event(bot, event)

        ctx.should_pass_permission(matcher=test)
        ctx.should_pass_rule(matcher=test)
        ctx.should_not_pass_permission(matcher=test_not_pass_perm)
        ctx.should_pass_permission(matcher=test_not_pass_rule)
        ctx.should_not_pass_rule(matcher=test_not_pass_rule)
        ctx.should_ignore_permission()
        ctx.should_not_pass_rule()

        ctx.should_call_send(event, "test_send", "result", bot=bot)
        ctx.should_call_api("test", {"key": "value"}, "result", adapter=adapter)
        ctx.should_paused(matcher=test)

        event = make_fake_event(_message=Message())()
        ctx.receive_event(bot, event)

        ctx.should_pass_permission(matcher=test)
        ctx.should_pass_rule(matcher=test)

        ctx.should_rejected(matcher=test)

    async with app.test_matcher(test_ignore) as ctx:
        adapter = ctx.create_adapter()
        bot = ctx.create_bot(adapter=adapter)

        event = make_fake_event(_message=Message())()
        ctx.receive_event(bot, event)

        ctx.should_ignore_permission()
        ctx.should_ignore_rule()

        ctx.should_call_send(event, "key", "result", bot=bot)
        ctx.should_rejected()

        event = make_fake_event(_message=Message())()
        ctx.receive_event(bot, event)

        ctx.should_pass_permission()
        ctx.should_pass_rule()

        ctx.should_call_send(event, "message", "result", bot=bot)
        ctx.should_finished()


@pytest.mark.asyncio
@pytest.mark.xfail(strict=True)
async def test_error(app: App):
    from tests.plugins.process import test_error

    async with app.test_matcher(test_error) as ctx:
        adapter = ctx.create_adapter()
        bot = ctx.create_bot(adapter=adapter)

        event = make_fake_event()()
        ctx.receive_event(bot, event)

        ctx.should_call_send(event, "uncorrect", "result", bot=bot)
