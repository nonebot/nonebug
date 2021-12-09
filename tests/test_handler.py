from typing import TYPE_CHECKING, Type

import pytest
from pydantic import create_model

from nonebug import ProcessorApp

if TYPE_CHECKING:
    from nonebot.adapters import Event


def make_fake_event(**fields) -> Type["Event"]:
    from nonebot.adapters import Event, Message

    _Fake = create_model("_Fake", __base__=Event, **fields)

    class FakeEvent(_Fake):
        def get_type(self) -> str:
            return "test"

        def get_event_name(self) -> str:
            return "test"

        def get_event_description(self) -> str:
            return "test"

        def get_user_id(self) -> str:
            return "test"

        def get_session_id(self) -> str:
            return "test"

        def get_message(self) -> "Message":
            raise NotImplementedError

        def is_tome(self) -> bool:
            return True

        class Config:
            extra = "forbid"

    return FakeEvent


@pytest.mark.asyncio
async def test_handler(app: ProcessorApp):
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

    async with app.test_handler(_handle, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())
    async with app.test_handler(_handle_fake, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=FakeEvent())

    event = FakeEvent2()
    try:
        async with app.test_handler(_handle_fake, allow_types=[EventParam]) as ctx:
            ctx.pass_params(event=event)
    except SkippedException as e:
        assert e.param.name == "event"
        assert e.value is event
    else:
        assert False, "handler should be skipped"

    try:
        async with app.test_handler(_handle_return) as ctx:
            ctx.should_return(False)
    except AssertionError as e:
        pass
    else:
        assert False, "Handler return value should be checked"
