import sys

import pytest

from nonebug.helpers import clear_nonebot, clear_plugins


def test_clear_nonebot():
    import nonebot

    nonebot.init()

    clear_nonebot()

    assert not any(name for name in sys.modules if name.startswith("nonebot"))


def test_clear_builtin_plugins():
    import nonebot

    nonebot.init()
    nonebot.load_builtin_plugins("echo")

    assert "nonebot.plugins.echo" in sys.modules
    assert nonebot.get_plugin("echo")

    clear_plugins()

    assert "nonebot.plugins.echo" not in sys.modules

    clear_nonebot()


def test_clear_fixture(nonebug_clear: None):
    import nonebot

    nonebot.init()

    assert "nonebot" in sys.modules


@pytest.mark.order(after="test_clear_fixture")
def test_cleared():
    assert not any(name for name in sys.modules if name.startswith("nonebot"))