from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from nonebot.typing import T_State
    from nonebot.adapters import Bot, Event


@dataclass
class Model:
    ...


@dataclass
class ReceiveEvent(Model):
    bot: "Bot"
    event: "Event"
    state: "T_State"


@dataclass
class Paused(Model):
    ...


@dataclass
class Rejected(Model):
    ...


@dataclass
class Finished(Model):
    ...


@dataclass
class RulePass(Model):
    ...


@dataclass
class RuleNotPass(Model):
    ...


@dataclass
class IgnoreRule(Model):
    ...


@dataclass
class PermissionPass(Model):
    ...


@dataclass
class PermissionNotPass(Model):
    ...


@dataclass
class IgnorePermission(Model):
    ...
