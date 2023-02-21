import pytest
from utils import make_fake_event
from nonebot.adapters import Event
from nonebot.params import EventParam
from nonebot.exception import TypeMisMatch

from nonebug import App


@pytest.mark.asyncio
async def test_dependent(app: App):
    FakeEvent = make_fake_event(test_field=(str, "test"))
    FakeEvent2 = make_fake_event(test_field2=(str, "test2"))

    def _handle(event: Event):
        ...

    def _handle_fake(event: FakeEvent):  # type: ignore
        ...

    async with app.test_dependent(_handle, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())
    async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())

    event = FakeEvent2()
    with pytest.raises(TypeMisMatch) as e:
        async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
            ctx.pass_params(event=event)
    assert e.value.param.name == "event"
    assert e.value.value is event


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_should_fail(app: App):
    def _handle_return():
        return True

    async with app.test_dependent(_handle_return) as ctx:
        ctx.should_return(False)
