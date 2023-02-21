from typing import Set
from pathlib import Path

import pytest
import nonebot
from nonebot.plugin import Plugin

from nonebug.fixture import *
from nonebug import NONEBOT_INIT_KWARGS


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {"custom_key": "custom_value"}


@pytest.fixture(scope="session")
def load_plugin(nonebug_init: None) -> Set[Plugin]:
    return nonebot.load_plugins(str(Path(__file__).parent / "plugins"))
