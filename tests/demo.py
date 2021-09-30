import nonebot
import os
import sys
import nonebug
from nonebug import Constructor


sys.path.insert(0, os.path.abspath(".."))
nonebug.init(_env_file="tests/.env.prod")
nonebot.load_plugin("test_plugin")
con = Constructor("cqhttp testcase1", 'cqhttp', '123456')
con.set_message("123456", 12345)
con.add_mock_api('send_msg', {'message_id': 123456})
con.add_api('send_group_msg', {'group_id': 12345,
            "message": "1234"}, {'message_id': 1243456})
con.add_mock_api('send_private_msg', {'message_id': 1123456})
con1 = Constructor.load_from_toml("tests/demo.toml")
con2 = Constructor("cqhttp testmatcher",'CQHTTP','123')
con2.set_message("123", 123)
con2.add_api('send_msg', {'group_id':1234,'message':'test matcher'},{'message_id':123})


if __name__ == '__main__':
    import asyncio
    asyncio.run(con.run())
    asyncio.run(con1.run(log_name="demo1"))
    asyncio.run(con2.test_plugin("test_plugin1"))
    from test_plugin1 import hello1
    asyncio.run(con2.run(matchers=[hello1]))