import pytest

from nonebug.processor import App


def test_should_call_api(processor_app: App):
    api = processor_app.should_call_api("test", {"data": "data"}, "result")
    assert not processor_app.wait_list.empty()
    assert api == processor_app.wait_list.get()


def test_should_call_send(processor_app: App):
    from nonebot.adapters import Event, Message, MessageSegment

    class TestEvent(Event):
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

    send = processor_app.should_call_send(TestEvent(), "test message")
    assert not processor_app.wait_list.empty()
    assert send == processor_app.wait_list.get()
