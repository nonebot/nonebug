from exceptiongroup import BaseExceptionGroup
from nonebot.adapters import Event
from nonebot.exception import TypeMisMatch
from nonebot.params import EventParam
import pytest

from nonebug import App
from tests.utils import make_fake_event


@pytest.mark.asyncio
async def test_dependent(app: App):
    FakeEvent = make_fake_event(test_field=(str, "test"))
    FakeEvent2 = make_fake_event(test_field2=(str, "test2"))

    def _handle(event: Event): ...

    def _handle_fake(event: FakeEvent):  # type: ignore
        ...

    async with app.test_dependent(_handle, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())
    async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())

    event = FakeEvent2()
    with pytest.raises((TypeMisMatch, BaseExceptionGroup)) as exc_info:
        async with app.test_dependent(_handle_fake, allow_types=[EventParam]) as ctx:
            ctx.pass_params(event=event)

    if isinstance(exc_info.value, BaseExceptionGroup):
        assert exc_info.group_contains(TypeMisMatch)
        exc_group = exc_info.value.subgroup(TypeMisMatch)
        e = exc_group.exceptions[0] if exc_group else None
        assert isinstance(e, TypeMisMatch)
    else:
        e = exc_info.value

    assert e.param.name == "event"
    assert e.value is event


@pytest.mark.asyncio
@pytest.mark.xfail(strict=True)
async def test_should_fail(app: App):
    def _handle_return():
        return True

    async with app.test_dependent(_handle_return) as ctx:
        ctx.should_return(False)
