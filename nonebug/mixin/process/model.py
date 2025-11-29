from typing import TYPE_CHECKING, Union, ClassVar, Optional
from dataclasses import dataclass

from _pytest.outcomes import OutcomeException

if TYPE_CHECKING:
    from nonebot.matcher import Matcher
    from nonebot.adapters import Bot, Event


@dataclass
class Model: ...


@dataclass
class ReceiveEvent(Model):
    bot: "Bot"
    event: "Event"


@dataclass
class Action(Model):
    matcher: Optional[type["Matcher"]] = None


@dataclass
class Paused(Action): ...


@dataclass
class Rejected(Action): ...


@dataclass
class Finished(Action): ...


@dataclass
class Check(Model):
    matcher: Optional[type["Matcher"]] = None

    _priority: ClassVar[int]

    @property
    def priority(self) -> int:
        return self._priority + 100 * (self.matcher is None)


@dataclass
class RulePass(Check):
    _priority: ClassVar[int] = 3


@dataclass
class RuleNotPass(Check):
    _priority: ClassVar[int] = 2


@dataclass
class IgnoreRule(Check):
    _priority: ClassVar[int] = 1


@dataclass
class PermissionPass(Check):
    _priority: ClassVar[int] = 3


@dataclass
class PermissionNotPass(Check):
    _priority: ClassVar[int] = 2


@dataclass
class IgnorePermission(Check):
    _priority: ClassVar[int] = 1


@dataclass
class Error:
    matcher: type["Matcher"]
    error: Union[Exception, OutcomeException]
