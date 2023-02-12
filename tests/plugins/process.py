from nonebot import on_message
from nonebot.adapters import Bot
from nonebot.permission import Permission

test = on_message(rule=lambda: True, permission=Permission(lambda: True))


@test.handle()
async def _(bot: Bot):
    result = await test.send("test_send")
    assert result == "result"
    result = await bot.call_api("test", key="value")
    assert result == "result"
    await test.pause()


@test.handle()
async def _():
    await test.reject()


test_not_pass_perm = on_message(rule=lambda: True, permission=Permission(lambda: False))
test_not_pass_rule = on_message(rule=lambda: False, permission=Permission(lambda: True))


test_ignore = on_message(rule=lambda: False, permission=Permission(lambda: False))


@test_ignore.permission_updater
async def _():
    return Permission(lambda: True)


@test_ignore.got("key", prompt="key")
async def _():
    await test_ignore.finish("message")
