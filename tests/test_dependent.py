import pytest
from utils import make_fake_event

from nonebug.fixture import *
from nonebug import ProcessorApp


@pytest.mark.asyncio
async def test_dependent(app: "ProcessorApp"):
    from nonebot.adapters import Event
    from nonebot.params import EventParam
    from nonebot.exception import SkippedException

    FakeEvent = make_fake_event(test_field=(str, "test"))
    FakeEvent2 = make_fake_event(test_field2=(str, "test2"))

    def _handle(event: Event):
        ...

    def _handle_fake(event: FakeEvent):
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
    except SkippedException as e:
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
