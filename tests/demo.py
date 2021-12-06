import nonebot
import os
import sys
import nonebug
from nonebug import Constructor


sys.path.insert(0, os.path.abspath(".."))
nonebug.init(_env_file="tests/.env.prod")
nonebot.load_plugin("test_plugin")
con = Constructor("cqhttp testcase1", 'cqhttp', '123456')
con.set_message("123456", 12345,group_id=1234)
con.should_call_api('send_group_msg', {'group_id': 12345,
            "message": "1234"}, {'message_id': 1243456})
con.mock_api('send_private_msg', {'message_id': 1123456})
con1 = Constructor.load_from_toml("tests/demo.toml")
con2 = Constructor("cqhttp testmatcher",'CQHTTP','123')
con2.set_message("123", 123)
con2.should_call_api('send_msg', {'group_id':1234,'message':'test matcher'},{'message_id':123})




if __name__ == '__main__':
    con.run()
    con1.run()
    #asyncio.run(con2.test_plugin("test_plugin1"))
    from test_plugin1 import hello1
    con2.run(matchers=[hello1])