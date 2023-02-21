from typing import Set
from pathlib import Path

import pytest
import nonebot
from nonebot.plugin import Plugin

from nonebug.fixture import *


@pytest.fixture(scope="session")
def load_plugin(nonebug_init: None) -> Set[Plugin]:
    return nonebot.load_plugins(str(Path(__file__).parent / "plugins"))
