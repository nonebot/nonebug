from typing import Any

import pytest

NONEBOT_INIT_KWARGS = pytest.StashKey[dict[str, Any]]()
NONEBOT_START_LIFESPAN = pytest.StashKey[bool]()

from .app import App as App
