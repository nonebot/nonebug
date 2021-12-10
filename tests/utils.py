from pathlib import Path
from typing import TYPE_CHECKING, Set, Type

import pytest
from pydantic import create_model

from nonebug.fixture import *

if TYPE_CHECKING:
    from nonebot.plugin import Plugin
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


@pytest.fixture
def load_plugin(nonebug_init: None) -> Set["Plugin"]:
    import nonebot

    return nonebot.load_plugins(str(Path(__file__).parent / "plugins"))
