from typing import Type

from pydantic import create_model
from nonebot.adapters import Event, Message


def make_fake_event(**fields) -> Type[Event]:
    _Fake = create_model("_Fake", __base__=Event, **fields)

    class FakeEvent(_Fake):
        def get_type(self) -> str:
            return "message"

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
