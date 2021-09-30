import nonebot
import tomlkit
import importlib
from nonebot.matcher import Matcher
from nonebot.adapters import Event
from nonebot.adapters.cqhttp import Bot as CQHTTPBot, MessageSegment, Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.cqhttp.event import Sender
from nonebot.adapters.ding import Bot as DingBot
from nonebot.adapters.feishu import Bot as FeishuBot
from nonebot.adapters.mirai import Bot as MiraiBot
from nonebug.models import TestCase, Api
from nonebug.typing import Union, Optional, List, Type
from nonebug.models.cqhttp import get_cqhttp_api
from nonebug.handle import handle_testcase


class Constructor:
    def __init__(self, name: str, bot_type: str, bot_id: str) -> None:
        if bot_type.lower() == "cqhttp":
            self.bot = CQHTTPBot(bot_id, None)
        elif bot_type.lower() == "ding":
            self.bot = DingBot(bot_id, None)
        elif bot_type.lower() == "feishu":
            self.bot = FeishuBot(bot_id, None)
        elif bot_type.lower() == "mirai":
            self.bot = MiraiBot(bot_id, None)
        else:
            raise ValueError("bot_type only can be cqhttp,ding,feishu,mirai")
        self.name = name
        self.api_list = []

    def set_event(self, event: Event) -> None:
        self.event = event

    def set_message(self, message: Union[str, MessageSegment, Message], user_id: int,
                    nickname: str = "test_user", to_me: bool = False,
                    group_id: Optional[int] = None, role: Optional[str] = None,
                    card: Optional[str] = None, title: Optional[str] = None,
                    raw_message: Optional[str] = None, **kwargs) -> None:
        if not isinstance(self.bot, CQHTTPBot):
            raise NotImplementedError(
                "send_message is not supported in non-CQHTTP adapter，please use set_event.")
        kwargs['self_id'] = self.bot.self_id
        kwargs['post_type'] = "message"
        kwargs['sender'] = Sender(
            user_id=user_id, nickname=nickname, role=role, card=card, title=title)
        kwargs['raw_message'] = raw_message if raw_message else str(
            message)  # 还原check_to_me之前的内容较为困难，所以由用户设定原始信息
        kwargs['font'] = kwargs.get("font", 0)
        kwargs['message_id'] = kwargs.get("message_id", 0)
        kwargs['time'] = kwargs.get("time", 0)
        kwargs['user_id'] = user_id
        kwargs['message'] = message
        if group_id != None:
            kwargs['group_id'] = group_id
            kwargs['to_me'] = to_me
            kwargs['sub_type'] = 'normal'
            kwargs['message_type'] = 'group'
            self.set_event(GroupMessageEvent.parse_obj(kwargs))
        else:
            kwargs['to_me'] = True
            kwargs['sub_type'] = 'friend'
            kwargs['message_type'] = 'private'
            self.set_event(PrivateMessageEvent.parse_obj(kwargs))

    def add_api_model(self, api: Api) -> None:
        self.api_list.append(api)

    def add_api(self, action: str, data: Optional[dict], result: Optional[dict], mock: bool = False) -> None:
        if isinstance(self.bot, CQHTTPBot):
            api_type = get_cqhttp_api(action)
        else:
            raise NotImplementedError(
                "add_api is not supported in non-cqhttp adapter, please use add_api_model instead")
        self.api_list.append(
            api_type(action=action, data=data, result=result, mock=mock))

    def add_mock_api(self, action: str, result: Optional[dict]) -> None:
        self.add_api(action, None, result, mock=True)

    @classmethod
    def load_from_toml(cls, path: str, encoding: str = "utf-8") -> 'Constructor':
        with open(path, 'r', encoding=encoding) as f:
            dic = tomlkit.parse(f.read())
        testcase_data = dic.get("testcase")
        if not testcase_data:
            raise ValueError("cannot find '[testcase]' in given .toml file!")
        template_file = testcase_data.get("template", "")
        data = {}
        if template_file:
            with open(template_file, 'r', encoding=encoding) as f:
                template_dic = tomlkit.parse(f.read())
            template_data = template_dic.get("template")
            if not testcase_data:
                raise ValueError(
                    "cannot find '[template]' in given .toml file!")
            data.update(**template_data)
        data['name'] = testcase_data.get("name", data['name'])
        data['bot_type'] = testcase_data.get("bot_type", data['bot_type'])
        data['bot_id'] = testcase_data.get("bot_id", data['bot_id'])
        try:
            data['event'].update(testcase_data.get("event", {}))
        except KeyError:
            data['event'] = testcase_data.get("event", {})
        try:
            data['api_list'].extend(testcase_data.get("api", []))
        except KeyError:
            data['api_list'] = testcase_data.get("api", [])
        self = cls(data['name'], data['bot_type'], data['bot_id'])
        event_name = data['event'].get("name", "")
        event_module = f"nonebot.adapters.{data['bot_type'].lower()}.event"
        module = importlib.import_module(event_module)
        if not hasattr(module, event_name):
            raise ValueError(
                f"{event_name} is not supported by {data['bot_type'].lower()}")
        event_model = getattr(module, event_name)
        event = event_model.parse_obj(data['event'])
        self.set_event(event)
        for api in data['api_list']:
            action = api.get("action", "")
            apidata = api.get("data")
            result = api.get("result")
            mock = api.get("mock", False)
            self.api_list.append(
                Api(action=action, data=apidata, result=result, mock=mock))
        return self

    async def run(self, *, log_output: bool = True, log_name: Optional[str] = None, matchers: Optional[List[Type["Matcher"]]] = None) -> None:
        if not self.event or not self.api_list:
            raise ValueError("event and api must be set to test!")
        testcase = TestCase(name=self.name, bot=self.bot,
                            event=self.event, api_list=self.api_list)
        await handle_testcase(testcase, log_output, log_name, matchers)
    
    
    async def test_plugin(self,plugin_name:str, *, log_output: bool = True, log_name: Optional[str] = None):
        if not self.event or not self.api_list:
            raise ValueError("event and api must be set to test!")
        testcase = TestCase(name=self.name, bot=self.bot,
                            event=self.event, api_list=self.api_list)
        flag = True
        plugin = nonebot.load_plugin(plugin_name)
        print(plugin)
        if plugin is None:
            plugin = nonebot.get_plugin(plugin_name)
            flag = False
        if plugin is None:
            raise ValueError(f"{plugin_name} cannot be loaded by nonebot, please check!")
        matchers = list(plugin.matcher)
        print(matchers,plugin.matcher)
        await handle_testcase(testcase, log_output, log_name, matchers)
        if flag: #需要还原plugins
            from nonebot.plugin import plugins
            plugins.pop(plugin_name)
            