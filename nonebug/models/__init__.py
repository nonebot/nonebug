from pydantic import BaseModel
from nonebot.adapters import Bot, Event
from nonebug.typing import List, Optional


class Data(BaseModel):
    class Config:
        extra = "allow"


class Result(BaseModel):
    class Config:
        extra = "allow"


class Api(BaseModel):
    action: str
    data: Optional[Data] = None
    result: Optional[Result] = None
    mock: bool = False

    class Config:
        extra = "allow"


class TestCase:
    def __init__(self,name:str,bot:Bot,event:Event,api_list:List[dict]) -> None:
        self.name = name
        self.bot = bot
        self.event = event
        self.api_list = api_list
