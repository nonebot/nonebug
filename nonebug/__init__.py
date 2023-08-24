from typing import Any, Dict

import pytest

NONEBOT_INIT_KWARGS = pytest.StashKey[Dict[str, Any]]()

from .app import App as App
