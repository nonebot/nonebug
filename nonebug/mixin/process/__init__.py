from contextvars import ContextVar
from collections import defaultdict
from typing_extensions import final
from contextlib import contextmanager
from typing import Dict, List, Type, Tuple, Union, Optional, TypedDict

import pytest
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.message import handle_event

from nonebug.base import BaseApp
from nonebug.mixin.call_api import ApiContext

from .fake import make_fake_matcher
from .model import (
    Check,
    Action,
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

event_test_context: ContextVar[Tuple[ReceiveEvent, "EventTest"]] = ContextVar(
    "event_test_context"
)


class EventTest(TypedDict):
    checks: List[Check]
    actions: List[Action]


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
        self.event_list: List[Tuple[ReceiveEvent, EventTest]] = []

    @property
    def currect_event_test(self) -> EventTest:
        if not self.event_list:
            raise RuntimeError("Please call receive_event first")
        return self.event_list[-1][1]

    def receive_event(self, bot: Bot, event: Event) -> ReceiveEvent:
        receive_event = ReceiveEvent(bot, event)
        self.event_list.append((receive_event, EventTest(checks=[], actions=[])))
        return receive_event

    def should_pass_rule(self, matcher: Optional[Type[Matcher]] = None) -> RulePass:
        rule = RulePass(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def should_not_pass_rule(
        self, matcher: Optional[Type[Matcher]] = None
    ) -> RuleNotPass:
        rule = RuleNotPass(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def should_ignore_rule(self, matcher: Optional[Type[Matcher]] = None) -> IgnoreRule:
        rule = IgnoreRule(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def got_check_rule(self, matcher: Type[Matcher], result: bool) -> bool:
        context = event_test_context.get()
        event = context[0]
        checks = [
            c
            for c in context[1]["checks"]
            if isinstance(c, (RulePass, RuleNotPass, IgnoreRule))
        ]
        for check in checks:
            if check.matcher is matcher:
                if isinstance(check, RulePass):
                    assert (
                        result
                    ), f"{matcher} should pass rule check when receive {event}"
                elif isinstance(check, RuleNotPass):
                    assert (
                        not result
                    ), f"{matcher} should not pass rule check when receive {event}"
                elif isinstance(check, IgnoreRule):
                    result = True
                checks.remove(check)
                return result
            elif check.matcher is None:
                if isinstance(check, RulePass):
                    assert (
                        result
                    ), f"{matcher} should pass rule check when receive {event}"
                elif isinstance(check, RuleNotPass):
                    assert (
                        not result
                    ), f"{matcher} should not pass rule check when receive {event}"
                elif isinstance(check, IgnoreRule):
                    result = True
                return result
        return result

    def should_pass_permission(
        self, matcher: Optional[Type[Matcher]] = None
    ) -> PermissionPass:
        permission = PermissionPass(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def should_not_pass_permission(
        self, matcher: Optional[Type[Matcher]] = None
    ) -> PermissionNotPass:
        permission = PermissionNotPass(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def should_ignore_permission(
        self, matcher: Optional[Type[Matcher]] = None
    ) -> IgnorePermission:
        permission = IgnorePermission(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def got_check_permission(self, matcher: Type[Matcher], result: bool) -> bool:
        context = event_test_context.get()
        event = context[0]
        checks = [
            c
            for c in context[1]["checks"]
            if isinstance(c, (PermissionPass, PermissionNotPass, IgnorePermission))
        ]
        for check in checks:
            if check.matcher is matcher:
                if isinstance(check, PermissionPass):
                    assert (
                        result
                    ), f"{matcher} should pass permission check when receive {event}"
                elif isinstance(check, PermissionNotPass):
                    assert (
                        not result
                    ), f"{matcher} should not pass permission check when receive {event}"
                elif isinstance(check, IgnorePermission):
                    result = True
                checks.remove(check)
                break
            elif check.matcher is None:
                if isinstance(check, PermissionPass):
                    assert (
                        result
                    ), f"{matcher} should pass permission check when receive {event}"
                elif isinstance(check, PermissionNotPass):
                    assert (
                        not result
                    ), f"{matcher} should not pass permission check when receive {event}"
                elif isinstance(check, IgnorePermission):
                    result = True
                break
        return result

    def should_paused(self, matcher: Optional[Type[Matcher]] = None) -> Paused:
        assert all(
            action.matcher is not matcher
            for action in self.currect_event_test["actions"]
        ), f"Should not set action twice for same matcher: {matcher}"
        paused = Paused(matcher=matcher)
        self.currect_event_test["actions"].append(paused)
        return paused

    def should_rejected(self, matcher: Optional[Type[Matcher]] = None) -> Rejected:
        assert all(
            action.matcher is not matcher
            for action in self.currect_event_test["actions"]
        ), f"Should not set action twice for same matcher: {matcher}"
        rejected = Rejected(matcher=matcher)
        self.currect_event_test["actions"].append(rejected)
        return rejected

    def should_finished(self, matcher: Optional[Type[Matcher]] = None) -> Finished:
        assert all(
            action.matcher is not matcher
            for action in self.currect_event_test["actions"]
        ), f"Should not set action twice for same matcher: {matcher}"
        finished = Finished(matcher=matcher)
        self.currect_event_test["actions"].append(finished)
        return finished

    @contextmanager
    def _prepare(self):
        with pytest.MonkeyPatch.context():
            yield

    def mock_matcher(self, monkeypatch: pytest.MonkeyPatch):
        fake_matcher = make_fake_matcher(self)
        for attr in ("check_perm", "check_rule"):
            monkeypatch.setattr(Matcher, attr, getattr(fake_matcher, attr))

    async def setup(self) -> None:
        await super().setup()
        self.stack.enter_context(self.app.provider.context(self.matchers))

    async def run(self):
        while self.event_list:
            event, context = self.event_list.pop(0)
            context["checks"].sort(key=lambda x: x.priority, reverse=True)
            t = event_test_context.set((event, context))
            try:
                await handle_event(bot=event.bot, event=event.event)

                if remain := [c for c in context["checks"] if c.matcher]:
                    raise AssertionError(
                        f"Some checks remain after receive event {event}: {remain}"
                    )
            finally:
                event_test_context.reset(t)


class ProcessMixin(BaseApp):
    def test_matcher(
        self,
        m: Union[Type[Matcher], List[Type[Matcher]], Dict[int, List[Type[Matcher]]]],
        /,
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
