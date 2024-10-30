from pathlib import Path

import pytest
import nonebot
from nonebot.plugin import Plugin

from nonebug import NONEBOT_INIT_KWARGS
from nonebug.fixture import *  # noqa: F403


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {"custom_key": "custom_value"}


@pytest.fixture(scope="session", autouse=True)
async def after_nonebot_init(_nonebot_init: None) -> set[Plugin]:
    return nonebot.load_plugins(str(Path(__file__).parent / "plugins"))
