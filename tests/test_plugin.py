from nonebot.adapters.cqhttp import Bot,LifecycleMetaEvent
from nonebot import on_metaevent
from loguru import logger
hello = on_metaevent()

@hello.handle()
async def _(bot:Bot,event:LifecycleMetaEvent):
    res = await bot.send_msg(group_id=1234,message="123")
    logger.info(res["message_id"])
    