from typing import TYPE_CHECKING, Type

from pydantic import create_model

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
