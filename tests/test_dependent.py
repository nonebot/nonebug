import pytest
from utils import make_fake_event

from nonebug import App
from nonebug.fixture import *


@pytest.mark.asyncio
async def test_dependent(app: App):
    from nonebot.adapters import Event
    from nonebot.params import EventParam
    from nonebot.exception import TypeMisMatch

    FakeEvent = make_fake_event(test_field=(str, "test"))
    FakeEvent2 = make_fake_event(test_field2=(str, "test2"))

    def _handle(event: Event):
        ...

    def _handle_fake(event: FakeEvent):  # type: ignore
        ...

    def _handle_return():
        return True

    async with app.test_dependent(_handle, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())
    async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())

    event = FakeEvent2()
    try:
        async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
            ctx.pass_params(event=event)
    except TypeMisMatch as e:
        assert e.param.name == "event"
        assert e.value is event
    else:
        assert False, "handler should be skipped"

    try:
        async with app.test_dependent(_handle_return) as ctx:
            ctx.should_return(False)
    except AssertionError as e:
        pass
    else:
        assert False, "Handler return value should be checked"
