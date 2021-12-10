from nonebot import on_message

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
