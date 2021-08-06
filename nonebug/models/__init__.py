from pydantic import BaseModel
from nonebot.adapters import Bot, Event
from nonebug.typing import List


class Data(BaseModel):
    pass


class Result(BaseModel):
    pass


class Api(BaseModel):
    action: str
    data: Data
    result: Result


class TestCase(BaseModel):
    name: str
    bot: Bot
    event: Event
    api_list: List[Api]
    class Config:
        arbitrary_types_allowed = True