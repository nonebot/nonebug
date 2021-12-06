import sys

import pytest


def test_init(nonebug_init: None):
    assert "nonebot" in sys.modules

    import nonebot

    assert nonebot.get_driver()
