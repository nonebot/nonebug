import nonebot


def test_custom_init(nonebug_init):
    config = nonebot.get_driver().config

    assert config.custom_key == "custom_value"
