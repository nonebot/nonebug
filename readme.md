<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://raw.githubusercontent.com/nonebot/nonebot2/master/docs/.vuepress/public/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBug

_✨ NoneBot2  测试框架✨_

</div>



## 使用方法

1. 安装 `nonebug` 到您的 `nonebot2` 环境 
```
pip install nonebug
```
2. 我们可以假设有如下插件(假设命名为test_plugin)需要被 `nonebug` 测试：

```python
from nonebot.adapters.cqhttp import Bot,MessageEvent
from nonebot import on_message
from nonebot.log import logger
hello1 = on_message()

@hello1.handle()
async def _(bot:Bot,event:MessageEvent):
    res = await bot.send_msg(group_id=1234,message="test matcher")
    logger.info(res["message_id"])
```

3. 则可按如下办法来进行测试：

```python
import nonebot
import os
import sys
import nonebug
from nonebug import Constructor

nonebug.init()
con2 = Constructor("cqhttp testmatcher",'CQHTTP','123')
con2.set_message("123", 123)
con2.add_api('send_msg', {'group_id':1234,'message':'test matcher'},{'message_id':123})

if __name__ == '__main__':
import asyncio
asyncio.run(con2.test_plugin("test_plugin"))
```

   

## 进阶和文档

TODO