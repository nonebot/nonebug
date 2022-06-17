import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nonebot.plugin import Plugin


def clear_matchers() -> None:
    from nonebot.matcher import matchers

    for priority in matchers:
        for matcher in matchers[priority]:
            if not matcher.module_name:  # pragma: no cover
                continue
            clear_module_with_prefix(matcher.module_name)
    matchers.clear()


def clear_plugin(plugin: "Plugin") -> None:
    clear_module_with_prefix(plugin.module_name)


def clear_plugins() -> None:
    from nonebot.plugin import _plugins, _managers

    for plugin in _plugins.values():
        clear_plugin(plugin)
    _plugins.clear()
    _managers.clear()


def clear_logger() -> None:
    from nonebot.log import logger

    logger.remove()


def clear_module(module_name: str) -> None:
    if module_name in sys.modules:
        del sys.modules[module_name]


def clear_module_with_prefix(module_name: str) -> None:
    keys = [key for key in sys.modules if key.startswith(module_name)]
    for key in keys:
        clear_module(key)


def clear_nonebot() -> None:
    clear_matchers()
    clear_plugins()
    clear_logger()
    clear_module_with_prefix("nonebot")
