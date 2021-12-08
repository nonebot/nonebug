from typing import TYPE_CHECKING, Type

import pytest
from pydantic import create_model

from nonebug.processor import App

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


def test_should_call_api(processor_app: App):
    api = processor_app.should_call_api("test", {"data": "data"}, "result")
    queue = processor_app.wait_list
    assert not queue.empty()
    assert api == queue.get()
    assert (
        api.name == "test" and api.data == {"data": "data"} and api.result == "result"
    )


def test_should_call_send(processor_app: App):
    event = make_fake_event()()
    send = processor_app.should_call_send(event, "test message", "result")
    queue = processor_app.wait_list
    assert not queue.empty()
    assert send == queue.get()
    assert (
        send.event is event
        and send.message == "test message"
        and send.result == "result"
    )


def test_got_call_api(processor_app: App):
    api = processor_app.should_call_api("test", {"data": "data"}, "result")
    result = processor_app.got_call_api("test", {"data": "data"})
    assert processor_app.wait_list.empty()
    assert result == "result"


@pytest.mark.asyncio
async def test_handler(app: App):
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

    async with app.test_handler(_handle, allow_types=[EventParam], event=FakeEvent()):
        ...
    async with app.test_handler(
        _handle_fake, allow_types=[EventParam], event=FakeEvent()
    ):
        ...

    event = FakeEvent2()
    try:
        async with app.test_handler(
            _handle_fake, allow_types=[EventParam], event=event
        ):
            ...
    except SkippedException as e:
        assert e.param.name == "event"
        assert e.value is event
    else:
        assert False, "handler should be skipped"

    try:
        async with app.test_handler(_handle_return):
            app.should_return(False)
    except AssertionError as e:
        pass
    else:
        assert False, "Handler return value should be checked"
