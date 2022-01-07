from nonebot import on_message
from nonebot.permission import Permission

test = on_message()


@test.handle()
async def _():
    ...


test_pause = on_message()


@test_pause.handle()
async def _():
    await test_pause.pause()


@test_pause.handle()
async def _():
    await test_pause.pause()


test_reject = on_message()


@test_reject.handle()
async def _():
    await test_reject.reject()


test_finish = on_message()


@test_finish.handle()
async def _():
    await test_finish.finish("message")


test_rule_permission_pass = on_message(
    rule=lambda: True, permission=Permission(lambda: True)
)


@test_rule_permission_pass.handle()
async def _():
    pass


test_rule_permission_not_pass = on_message(
    rule=lambda: False, permission=Permission(lambda: False)
)


@test_rule_permission_not_pass.handle()
async def _():
    pass


test_monkeypatch = on_message()


@test_monkeypatch.permission_updater
async def _():
    return Permission(lambda: False)


@test_monkeypatch.handle()
async def _():
    await test_monkeypatch.reject()
