from contextvars import ContextVar
from collections import defaultdict
from typing_extensions import final
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Type,
    Tuple,
    Union,
    Literal,
    Optional,
    TypedDict,
)

import pytest
from _pytest.outcomes import Skipped

from nonebug.base import BaseApp
from nonebug.mixin.call_api import ApiContext

from .fake import PATCHES, make_fake_check_matcher, make_fake_default_state
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

if TYPE_CHECKING:
    from nonebot.matcher import Matcher
    from nonebot.adapters import Bot, Event

event_test_context: ContextVar[Tuple[ReceiveEvent, "EventTest"]] = ContextVar(
    "event_test_context"
)


class EventTest(TypedDict):
    checks: List[Check]
    actions: List[Action]


@final
class MatcherContext(ApiContext):
    """Matcher testing context.

    This context is used to test the behavior of matcher(s).
    You can give specific matchers to test, or test all available matchers.

    Note:
        API testing is also available in this context.

        The matcher behavior should be defined immediately
        after the `MatcherContext.receive_event` call.
    """

    def __init__(
        self,
        app: "ProcessMixin",
        *args,
        matchers: Optional[Dict[int, List[Type["Matcher"]]]],
        **kwargs,
    ):
        super(MatcherContext, self).__init__(app, *args, **kwargs)
        self.matchers = matchers
        self.event_list: List[Tuple[ReceiveEvent, EventTest]] = []
        self.errors = []

    @property
    def currect_event_test(self) -> EventTest:
        if not self.event_list:
            raise RuntimeError("Please call receive_event first")
        return self.event_list[-1][1]

    def receive_event(self, bot: "Bot", event: "Event") -> ReceiveEvent:
        receive_event = ReceiveEvent(bot, event)
        self.event_list.append((receive_event, EventTest(checks=[], actions=[])))
        return receive_event

    def should_pass_rule(self, matcher: Optional[Type["Matcher"]] = None) -> RulePass:
        rule = RulePass(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def should_not_pass_rule(
        self, matcher: Optional[Type["Matcher"]] = None
    ) -> RuleNotPass:
        rule = RuleNotPass(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def should_ignore_rule(
        self, matcher: Optional[Type["Matcher"]] = None
    ) -> IgnoreRule:
        rule = IgnoreRule(matcher=matcher)
        self.currect_event_test["checks"].append(rule)
        return rule

    def got_check_rule(self, matcher: Type["Matcher"], result: bool) -> bool:
        context = event_test_context.get()
        event = context[0]
        checks = [
            c
            for c in context[1]["checks"]
            if isinstance(c, (RulePass, RuleNotPass, IgnoreRule))
        ]
        for check in checks:
            if check.matcher is matcher or check.matcher is None:
                if isinstance(check, RulePass):
                    if not result:
                        pytest.fail(
                            f"{matcher} should pass rule check when receive {event}"
                        )
                elif isinstance(check, RuleNotPass):
                    if result:
                        pytest.fail(
                            f"{matcher} should not pass rule check when receive {event}"
                        )
                elif isinstance(check, IgnoreRule):
                    result = True

                if check.matcher is matcher:
                    context[1]["checks"].remove(check)
                break
        return result

    def should_pass_permission(
        self, matcher: Optional[Type["Matcher"]] = None
    ) -> PermissionPass:
        permission = PermissionPass(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def should_not_pass_permission(
        self, matcher: Optional[Type["Matcher"]] = None
    ) -> PermissionNotPass:
        permission = PermissionNotPass(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def should_ignore_permission(
        self, matcher: Optional[Type["Matcher"]] = None
    ) -> IgnorePermission:
        permission = IgnorePermission(matcher=matcher)
        self.currect_event_test["checks"].append(permission)
        return permission

    def got_check_permission(self, matcher: Type["Matcher"], result: bool) -> bool:
        context = event_test_context.get()
        event = context[0]
        checks = [
            c
            for c in context[1]["checks"]
            if isinstance(c, (PermissionPass, PermissionNotPass, IgnorePermission))
        ]
        for check in checks:
            if check.matcher is matcher or check.matcher is None:
                if isinstance(check, PermissionPass):
                    if not result:
                        pytest.fail(
                            f"{matcher} should pass permission check when receive {event}"
                        )
                elif isinstance(check, PermissionNotPass):
                    if result:
                        pytest.fail(
                            f"{matcher} should not pass permission check when receive {event}"
                        )
                elif isinstance(check, IgnorePermission):
                    result = True

                if check.matcher is matcher:
                    context[1]["checks"].remove(check)
                break
        return result

    def should_paused(self, matcher: Optional[Type["Matcher"]] = None) -> Paused:
        if any(
            action.matcher is matcher for action in self.currect_event_test["actions"]
        ):
            pytest.fail(f"Should not set action twice for same matcher: {matcher}")
        paused = Paused(matcher=matcher)
        self.currect_event_test["actions"].append(paused)
        return paused

    def should_rejected(self, matcher: Optional[Type["Matcher"]] = None) -> Rejected:
        if any(
            action.matcher is matcher for action in self.currect_event_test["actions"]
        ):
            pytest.fail(f"Should not set action twice for same matcher: {matcher}")
        rejected = Rejected(matcher=matcher)
        self.currect_event_test["actions"].append(rejected)
        return rejected

    def should_finished(self, matcher: Optional[Type["Matcher"]] = None) -> Finished:
        if any(
            action.matcher is matcher for action in self.currect_event_test["actions"]
        ):
            pytest.fail(f"Should not set action twice for same matcher: {matcher}")
        finished = Finished(matcher=matcher)
        self.currect_event_test["actions"].append(finished)
        return finished

    def got_action(
        self, matcher: Type["Matcher"], action: Literal["pause", "reject", "finish"]
    ):
        context = event_test_context.get()
        event = context[0]
        actions = context[1]["actions"]
        for act in actions:
            if act.matcher is matcher or act.matcher is None:
                if isinstance(act, Paused):
                    if action != "pause":
                        pytest.fail(f"{matcher} should pause when receive {event}")
                elif isinstance(act, Rejected):
                    if action != "reject":
                        pytest.fail(f"{matcher} should reject when receive {event}")
                elif isinstance(act, Finished):
                    if action != "finish":
                        pytest.fail(f"{matcher} should finish when receive {event}")

                if act.matcher is matcher:
                    context[1]["actions"].remove(act)
                break

    @contextmanager
    def _prepare_matcher_context(self):
        import nonebot.message
        from nonebot.matcher import Matcher

        with self.app.provider.context(self.matchers) as provider:
            with pytest.MonkeyPatch.context() as m:
                m.setattr(
                    nonebot.message,
                    "_check_matcher",
                    make_fake_check_matcher(self, nonebot.message._check_matcher),
                )
                self.patch_matcher(m, Matcher)
                for matchers in provider.values():
                    for matcher in matchers:
                        m.setattr(
                            matcher,
                            "_default_state",
                            make_fake_default_state(self, matcher),
                        )
                yield

    def patch_matcher(self, monkeypatch: pytest.MonkeyPatch, matcher: Type["Matcher"]):
        for attr, patch_func in PATCHES.items():
            monkeypatch.setattr(matcher, attr, patch_func(self, matcher))

    async def setup(self) -> None:
        await super().setup()
        self.stack.enter_context(self._prepare_matcher_context())

    async def run(self):
        from nonebot.message import handle_event

        while self.event_list:
            event, context = self.event_list.pop(0)
            context["checks"].sort(key=lambda x: x.priority)
            context["actions"].sort(key=lambda x: x.matcher is None)
            t = event_test_context.set((event, context))
            try:
                await handle_event(bot=event.bot, event=event.event)

                if self.errors:
                    if any(isinstance(e, Skipped) for e in self.errors):
                        pytest.skip(
                            f"Check skipped when handling event {event}: {self.errors}"
                        )
                    pytest.fail(
                        f"Some checks failed when handling event {event}: {self.errors}"
                    )
                if remain_checks := [c for c in context["checks"] if c.matcher]:
                    pytest.fail(
                        f"Some checks remain after receive event {event}: {remain_checks}"
                    )
                if remain_actions := [a for a in context["actions"] if a.matcher]:
                    pytest.fail(
                        f"Some actions remain after receive event {event}: {remain_actions}"
                    )
            finally:
                self.errors.clear()
                event_test_context.reset(t)


class ProcessMixin(BaseApp):
    def test_matcher(
        self,
        m: Union[
            None,
            Type["Matcher"],
            List[Type["Matcher"]],
            Dict[int, List[Type["Matcher"]]],
        ] = None,
        /,
    ) -> MatcherContext:
        matchers: Optional[Dict[int, List[Type["Matcher"]]]]
        if m is None:
            matchers = None
        elif isinstance(m, list):
            matchers = defaultdict(list)
            for matcher in m:
                matchers[matcher.priority].append(matcher)
        elif isinstance(m, dict):
            matchers = m
        else:
            matchers = {m.priority: [m]}
        return MatcherContext(self, matchers=matchers)
