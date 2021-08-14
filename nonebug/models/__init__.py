from pydantic import BaseModel
from nonebot.adapters import Bot, Event
from nonebug.typing import List,Optional


class Data(BaseModel):
    class Config:
        extra = "allow"

class Result(BaseModel):
    class Config:
        extra = "allow"

class Api(BaseModel):
    action: str
    data: Optional[Data]=None
    result: Result
    mock : bool = False
    class Config:
        extra = "allow"


class TestCase(BaseModel):
    name: str
    bot: Bot
    event: Event
    api_list: List[Api]
    class Config:
        arbitrary_types_allowed = True
    
    