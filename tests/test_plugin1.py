from nonebot.adapters.cqhttp import Bot,MessageEvent
from nonebot import on_message
from nonebot.log import logger
hello1 = on_message()

@hello1.handle()
async def _(bot:Bot,event:MessageEvent):
    res = await bot.send_msg(group_id=1234,message="test matcher")
    logger.info(res["message_id"])