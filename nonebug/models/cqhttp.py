import inspect
from pydantic.main import BaseModel
from nonebug.typing import Literal, Optional, Union, Type, List
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.adapters.cqhttp.event import Anonymous, Sender
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


class DeleteMsgData(Data):
    message_id: int


class DeleteMsg(CQApi):
    __action__ = 'delete_msg'
    data: Optional[DeleteMsgData] = None



class GetMsgData(Data):
    message_id: int


class GetMsgResult(Result):
    time: int
    message_type: str
    message_id: int
    real_id: int
    sender: Sender
    message: Message


class GetMsg(CQApi):
    __action__ = 'get_msg'
    data: Optional[GetMsgData] = None
    result: GetMsgResult


class GetForwardMsgData(Data):
    message_id: str


class GetForwardMsgResult(Result):
    message: Message


class GetForwardMsg(CQApi):
    __action__ = 'get_forward_msg'
    data: Optional[GetForwardMsgData] = None
    result: GetForwardMsgResult


class SendLikeData(Data):
    user_id: int
    times: int


class SendLike(CQApi):
    __action__ = 'send_like'
    data: Optional[SendLikeData] = None



class SetGroupKickData(Data):
    group_id: int
    user_id: int
    reject_add_request: bool = False


class SetGroupKick():
    __action__ = 'set_group_kick'
    data: Optional[SetGroupKickData] = None



class SetGroupBanData(Data):
    group_id: int
    user_id: int
    duration: int = 1800


class SetGroupBan(CQApi):
    __action__ = 'set_group_ban'
    data: Optional[SetGroupBanData] = None



class SetGroupAnonymousBanData(Data):
    group_id: int
    anonymous: Anonymous
    anonymous_flag: Optional[str] = None
    duration: int = 1800


class SetGroupAnonymousBan(CQApi):
    __action__ = 'set_group_anonymous_ban'
    data: Optional[SetGroupAnonymousBanData] = None



class SetGroupWholeBanData(Data):
    group_id: int
    enable: bool = True


class SetGroupWholeBan(CQApi):
    __action__ = 'set_group_whole_ban'
    data: Optional[SetGroupWholeBanData] = None



class SetGroupAdminData(Data):
    group_id: int
    user_id: int
    enable: bool = True


class SetGroupAdmin(CQApi):
    __action__ = 'set_group_admin'
    data: Optional[SetGroupAdminData] = None



class SetGroupAnonymousData(Data):
    group_id: int
    enable: bool = True


class SetGroupAnonymous(CQApi):
    __action__ = 'set_group_anonymous'
    data: Optional[SetGroupAnonymousData] = None



class SetGroupCardData(Data):
    group_id: int
    user_id: int
    card: Optional[str] = None


class SetGroupCard(CQApi):
    __action__ = 'set_group_card'
    data: Optional[SetGroupCardData] = None



class SetGroupNameData(Data):
    group_id: int
    group_name: str


class SetGroupName(CQApi):
    __action__ = 'set_group_name'
    data: Optional[SetGroupNameData] = None



class SetGroupLeaveData(Data):
    group_id: int
    is_dismiss: bool = False


class SetGroupLeave(CQApi):
    __action__ = 'set_group_leave'
    data: Optional[SetGroupLeaveData] = None



class SetGroupSpecialTitleData(Data):
    group_id: int
    user_id: int
    special_title: Optional[str] = None
    duration: int = -1


class SetGroupSpecialTitle(CQApi):
    __action__ = 'set_group_special_title'
    data: Optional[SetGroupSpecialTitleData] = None



class SetFriendAddRequestData(Data):
    flag: str
    approve: bool = True
    remark: Optional[str] = None


class SetFriendAddRequest(CQApi):
    __action__ = 'set_friend_add_request'
    data: Optional[SetFriendAddRequestData] = None



class SetGroupAddRequestData(Data):
    flag: str
    sub_type: str
    approve: bool = True
    reason: Optional[str] = None


class SetGroupAddRequest(CQApi):
    __action__ = 'set_group_add_request'
    data: Optional[SetGroupAddRequestData] = None



class GetLoginInfoResult(Result):
    user_id: int
    nickname: str


class GetLoginInfo(CQApi):
    __action__ = 'get_login_info'
    result: GetLoginInfoResult


class GetStrangerInfoData(Data):
    user_id: int
    no_cache: bool = False


class GetStrangerInfoResult(Result):
    user_id: int
    nickname: str
    sex: Literal['male', 'female', 'unknown']
    age: int


class GetStrangerInfo(CQApi):
    __action__ = 'get_stranger_info'
    data: Optional[GetStrangerInfoData] = None
    result: GetStrangerInfoResult


class GetFriendListResult(Result):
    user_id: int
    nickname: str
    remark: str


class GetFriendList(CQApi):
    __action__ = 'get_friend_list'
    result: List[GetFriendListResult]


class GetGroupInfoData(Data):
    group_id: int
    no_cache: bool = False


class GetGroupInfoResult(Result):
    group_id: int
    group_name: str
    member_count: int
    max_member_count: int


class GetGroupInfo(CQApi):
    __action__ = 'get_group_info'
    data: Optional[GetGroupInfoData] = None
    result: GetGroupInfoResult


class GetGroupList(CQApi):
    __action__ = 'get_group_list'
    result: List[GetGroupInfoResult]


class GetGroupMemberInfoData(Data):
    group_id: int
    user_id: int
    no_cache: bool = False


class GetGroupMemberInfoResult(Result):
    group_id: int
    user_id: int
    nickname: str
    card: str
    sex: Literal['male', 'female', 'unknown']
    age: int
    area: str
    join_time: int
    last_sent_time: int
    level: str
    role: Literal['owner', 'admin', 'member']
    unfriendly: bool
    title: str
    title_expire_time: int
    card_changeable: bool


class GetGroupMemberInfo(CQApi):
    __action__ = 'get_group_member_info'
    data: Optional[GetGroupMemberInfoData] = None
    result: GetGroupMemberInfoResult


class GetGroupMemberListData(Data):
    group_id: int


class GetGroupMemberList(CQApi):
    __action__ = 'get_group_member_list'
    data: Optional[GetGroupMemberListData] = None
    result: List[GetGroupMemberInfoResult]


class CurrentTalkative(BaseModel):
    user_id: int
    nickname: str
    avatar: str
    day_count: int


class HonorElement(BaseModel):
    user_id: int
    nickname: str
    avatar: str
    description: str


class GetGroupHonorInfoData(Data):
    group_id: int
    type: Literal['talkative', 'performer',
                  'legend', 'strong_newbie', 'emotion', 'all']


class GetGroupHonorInfoResult(Result):
    group_id: int
    current_talkative: Optional[CurrentTalkative]
    talkative_list:  Optional[List[HonorElement]]
    performer_list:  Optional[List[HonorElement]]
    legend_list:  Optional[List[HonorElement]]
    strong_newbie_list:  Optional[List[HonorElement]]
    emotion_list:  Optional[List[HonorElement]]


class GetGroupHonorInfo(CQApi):
    __action__ = 'get_group_honor_info'
    data: Optional[GetGroupHonorInfoData] = None
    result: GetGroupHonorInfoResult


class GetCookiesData(Data):
    domain: str


class GetCookiesResult(Result):
    cookies: str


class GetCookies(CQApi):
    __action__ = 'get_cookies'
    data: Optional[GetCookiesData] = None
    result: GetCookiesResult


class GetCsrfTokenResult(Result):
    token: str


class GetCsrfToken(CQApi):
    __action__ = 'get_csrf_token'
    result: GetCsrfTokenResult


class GetCredentialsData(Data):
    domain: str


class GetCredentialsResult(Result):
    cookies: str
    csrf_token: str


class GetCredentials(CQApi):
    __action__ = 'get_credentials'
    data: Optional[GetCredentialsData] = None
    result: GetCredentialsResult


class GetRecordData(Data):
    file: str
    out_format: Literal['wav', 'mp3', 'flac',
                        'amr', 'm4a', 'ogg', 'spx', 'wma']


class GetRecordResult(Result):
    file: str


class GetRecord(CQApi):
    __action__ = 'get_record'
    data: Optional[GetRecordData] = None
    result: GetRecordResult


class GetImageData(Data):
    file: str


class GetImageResult(Result):
    file: str


class GetImage(CQApi):
    __action__ = 'get_image'
    data: Optional[GetImageData] = None
    result: GetImageResult


class CanSendImageResult(Result):
    yes: bool


class CanSendImage(CQApi):
    __action__ = 'can_send_image'
    result: CanSendImageResult


class CanSendRecordResult(Result):
    yes: bool


class CanSendRecord(CQApi):
    __action__ = 'can_send_record'
    result: CanSendRecordResult


class GetStatusResult(Result):
    online: Optional[bool]
    good: bool

    class Config:
        extra = "allow"


class GetStatus(CQApi):
    __action__ = 'get_status'
    result: GetStatusResult


class GetVersionInfoResult(Result):
    app_name: str
    app_version: str
    protocol_version: str

    class Config:
        extra = "allow"


class GetVersionInfo(CQApi):
    __action__ = 'get_version_info'
    result: GetVersionInfoResult


class SetRestartData(Data):
    delay: int = 0


class SetRestart(CQApi):
    __action__ = 'set_restart'
    data: Optional[SetRestartData] = None



class CleanCache(CQApi):
    __action__ = 'clean_cache'


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
