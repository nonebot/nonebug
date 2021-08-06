from typing import Literal, Optional, Union
from nonebot.adapters.cqhttp.message import Message, MessageSegment
from . import Api, Data, Result


class SendMsgData(Data):
    message_type: Optional[Literal['private', 'group']] = None
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    message: Union[Message, str, MessageSegment]
    autoescape: bool = False


class SendMsgResult(Result):
    message_id: int


class SendMsg(Api):
    action ='send_msg'
    data: SendMsgData
    result: SendMsgResult