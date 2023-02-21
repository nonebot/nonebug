from typing import Any, Dict

from pytest import StashKey

NONEBOT_INIT_KWARGS = StashKey[Dict[str, Any]]()

from .app import App as App
