import inspect
from nonebug.typing import Literal, Optional, Union, Type
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from . import Api, Data, Result


class CQApi(Api):
    __action__ = ''


class SendMsgData(Data):
    message_type: Optional[Literal['private', 'group']] = None
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    message: Union[str, MessageSegment, Message]
    autoescape: bool = False


class SendMsgResult(Result):
    message_id: int


class SendMsg(CQApi):
    __action__ = 'send_msg'
    data: Optional[SendMsgData] = None
    result: SendMsgResult


class SendGroupMsgData(SendMsgData):
    group_id: int
    message: Union[str, MessageSegment, Message]
    autoescape: bool = False


class SendGroupMsg(CQApi):
    __action__ = 'send_group_msg'
    data:  Optional[SendGroupMsgData] = None
    result: SendMsgResult


class SendPrivateMsgData(SendMsgData):
    user_id: int
    message: Union[str, MessageSegment, Message]
    autoescape: bool = False


class SendPrivateMsg(CQApi):
    __action__ = 'send_private_msg'
    data:  Optional[SendGroupMsgData] = None
    result: SendMsgResult


_apis = {}
api = None
for api in globals().values():
    if not inspect.isclass(api) or not issubclass(api, CQApi):
        continue
    _apis[api.__action__] = api


def get_cqhttp_api(action: str) -> Type[Api]:
    if action not in _apis:
        raise ValueError(f'{action} is not supported in cqhttp-adapter')
    return _apis[action]
