import asyncio
import time
import nonebot
from nonebot.adapters.cqhttp import Bot,LifecycleMetaEvent,Message
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
from nonebug import  handle_testcases
from nonebug.models import TestCase
from nonebug.models.cqhttp import SendMsg, SendMsgData, SendMsgResult
nonebot.init()
nonebot.load_plugin("test_plugin")
bot = Bot(1233,None)
event =LifecycleMetaEvent(
                meta_event_type="lifecycle",
                sub_type="hello_world",
                post_type="meta_event",
                time=time.time(),
                self_id=1233,
            )
data = SendMsgData(group_id=1234, message=Message("123"))
wrong_data = SendMsgData(group_id=1234, message=Message("123223"))
res = SendMsgResult(message_id=12345)
api = SendMsg(data=data,result=res)
api_1= SendMsg(data=wrong_data,result=res)
testcase = TestCase(name="first case",bot=bot,event=event,api_list=[api])
testcase1 = TestCase(name="second case",bot=bot,event=event,api_list=[api_1])
if __name__ == '__main__':
    asyncio.run(handle_testcases([testcase,testcase1]))
    