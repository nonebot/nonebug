from nonebug import Constructor
import nonebot
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
nonebot.init()
nonebot.load_plugin("test_plugin")
con = Constructor("cqhttp testcase1", 'cqhttp', '123456')
con.set_message("123456", 12345)
con.add_mock_api('send_msg', {'message_id': 123456})
con.add_api('send_group_msg', {'group_id': 12345,
            "message": "1234"}, {'message_id': 1243456})
con.add_mock_api('send_private_msg', {'message_id': 1123456})
con1 = Constructor.load_from_toml("demo.toml")
if __name__ == '__main__':
    import asyncio
    asyncio.run(con.run())
    asyncio.run(con1.run())
