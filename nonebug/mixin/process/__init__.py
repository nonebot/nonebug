from collections import defaultdict
from typing_extensions import final
from typing import Dict, List, Type, Union, Optional

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event

from nonebug.base import BaseApp

from ..call_api import ApiContext
from .model import (
    Model,
    Paused,
    Finished,
    Rejected,
    RulePass,
    IgnoreRule,
    RuleNotPass,
    ReceiveEvent,
    PermissionPass,
    IgnorePermission,
    PermissionNotPass,
)


@final
class MatcherContext(ApiContext):
    def __init__(
        self,
        app: "ProcessMixin",
        *args,
        matchers: Optional[Dict[int, List[Type[Matcher]]]],
        **kwargs,
    ):
        super(MatcherContext, self).__init__(app, *args, **kwargs)
        self.matchers = matchers
        self.action_list: List[Model] = []

    def receive_event(
        self, bot: Bot, event: Event, state: Optional[T_State] = None
    ) -> ReceiveEvent:
        receive_event = ReceiveEvent(bot, event, state or {})
        self.action_list.append(receive_event)
        return receive_event

    def should_pass_rule(self) -> RulePass:
        rule = RulePass()
        self.action_list.append(rule)
        return rule

    def should_not_pass_rule(self) -> RuleNotPass:
        rule = RuleNotPass()
        self.action_list.append(rule)
        return rule

    def should_ignore_rule(self) -> IgnoreRule:
        rule = IgnoreRule()
        self.action_list.append(rule)
        return rule

    def should_pass_permission(self) -> PermissionPass:
        permission = PermissionPass()
        self.action_list.append(permission)
        return permission

    def should_not_pass_permission(self) -> PermissionNotPass:
        permission = PermissionNotPass()
        self.action_list.append(permission)
        return permission

    def should_ignore_permission(self) -> IgnorePermission:
        permission = IgnorePermission()
        self.action_list.append(permission)
        return permission

    def should_paused(self) -> Paused:
        paused = Paused()
        self.action_list.append(paused)
        return paused

    def should_rejected(self) -> Rejected:
        rejected = Rejected()
        self.action_list.append(rejected)
        return rejected

    def should_finished(self) -> Finished:
        finished = Finished()
        self.action_list.append(finished)
        return finished

    async def setup(self) -> None:
        await super().setup()
        self.stack.enter_context(self.app.provider.context(self.matchers))

    async def run(self):
        ...


class ProcessMixin(BaseApp):
    def test_matcher(
        self,
        m: Union[Type[Matcher], List[Type[Matcher]], Dict[int, List[Type[Matcher]]]],
    ) -> MatcherContext:
        if isinstance(m, list):
            matchers: Dict[int, List[Type[Matcher]]] = defaultdict(list)
            for matcher in m:
                matchers[matcher.priority].append(matcher)
        elif isinstance(m, dict):
            matchers = m
        else:
            matchers = {m.priority: [m]}
        return MatcherContext(self, matchers=matchers)
