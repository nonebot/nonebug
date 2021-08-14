from nonebot.adapters.cqhttp import Bot,MessageEvent
from nonebot import on_message
from loguru import logger
hello = on_message()

@hello.handle()
async def _(bot:Bot,event:MessageEvent):
    res = await bot.send_msg(group_id=1234,message="123")
    logger.info(res["message_id"])
    res1 = await bot.send_group_msg(group_id=12345,message="1234")
    logger.info(res1["message_id"])
    res2 = await bot.send_private_msg(user_id=111111,message="11234")
    logger.info(res2["message_id"])