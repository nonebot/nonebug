from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, List, Type, Optional

from nonebug.base import BaseApp

from ..call_api import ApiContext
from .model import (
    Model,
    Paused,
    Finished,
    Rejected,
    RulePass,
    RuleNotPass,
    ReceiveEvent,
    PermissionPass,
    PermissionNotPass,
)

if TYPE_CHECKING:
    from nonebot.matcher import Matcher
    from nonebot.adapters import Bot, Event
    from nonebot.typing import T_State, T_DependencyCache


class MatcherContext(ApiContext):
    def __init__(self, app: "ProcessMixin", matcher: Type["Matcher"], *args, **kwargs):
        super(MatcherContext, self).__init__(app, *args, **kwargs)
        self.matcher_class = matcher
        self.matcher = matcher()
        self.action_list: List[Model] = []

    def receive_event(
        self, bot: "Bot", event: "Event", state: Optional["T_State"] = None
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

    def should_pass_permission(self) -> PermissionPass:
        permission = PermissionPass()
        self.action_list.append(permission)
        return permission

    def should_not_pass_permission(self) -> PermissionNotPass:
        permission = PermissionNotPass()
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

    async def run_test(self):
        from nonebot.matcher import current_handler
        from nonebot.exception import (
            PausedException,
            FinishedException,
            RejectedException,
        )

        stack = AsyncExitStack()
        dependency_cache: T_DependencyCache = {}
        async with stack:
            while self.action_list:
                # fake event received
                receive_event = self.action_list.pop(0)
                assert isinstance(
                    receive_event, ReceiveEvent
                ), f"Unexpected model {receive_event} expected ReceiveEvent"
                assert (
                    self.matcher.handlers
                ), f"Matcher has no handler remain, but received event {receive_event}"

                # test rule and permission
                rule_passed = await self.matcher.check_rule(
                    bot=receive_event.bot,
                    event=receive_event.event,
                    state=receive_event.state,
                    stack=stack,
                    dependency_cache=dependency_cache,
                )
                permission_passed = await self.matcher.check_perm(
                    bot=receive_event.bot,
                    event=receive_event.event,
                    stack=stack,
                    dependency_cache=dependency_cache,
                )
                while self.action_list and isinstance(
                    self.action_list[0],
                    (RulePass, RuleNotPass, PermissionPass, PermissionNotPass),
                ):
                    action = self.action_list.pop(0)
                    if isinstance(action, RulePass):
                        assert rule_passed, "Rule should be passed"
                    elif isinstance(action, RuleNotPass):
                        assert not rule_passed, "Rule should not be passed"
                    elif isinstance(action, PermissionPass):
                        assert permission_passed, "Permission should be passed"
                    elif isinstance(action, PermissionNotPass):
                        assert not permission_passed, "Permission should not be passed"

                if not rule_passed or not permission_passed:
                    continue

                try:
                    await self.matcher.simple_run(
                        bot=receive_event.bot,
                        event=receive_event.event,
                        state=receive_event.state,
                        stack=stack,
                    )
                except PausedException:
                    handler = current_handler.get()
                    if not self.action_list or isinstance(
                        self.action_list[0], ReceiveEvent
                    ):
                        continue
                    paused = self.action_list.pop(0)
                    assert isinstance(
                        paused, Paused
                    ), f"Matcher paused while running handler {handler} but got {paused}"
                    self.matcher.type = await self.matcher.update_type(
                        bot=receive_event.bot, event=receive_event.event
                    )
                    self.matcher.permission = await self.matcher.update_permission(
                        bot=receive_event.bot, event=receive_event.event
                    )
                except RejectedException:
                    handler = current_handler.get()
                    self.matcher.handlers.insert(0, handler)
                    if not self.action_list or isinstance(
                        self.action_list[0], ReceiveEvent
                    ):
                        continue
                    rejected = self.action_list.pop(0)
                    assert isinstance(
                        rejected, Rejected
                    ), f"Matcher rejected while running handler {handler} but got {rejected}"
                    self.matcher.type = await self.matcher.update_type(
                        bot=receive_event.bot, event=receive_event.event
                    )
                    self.matcher.permission = await self.matcher.update_permission(
                        bot=receive_event.bot, event=receive_event.event
                    )
                except FinishedException:
                    handler = current_handler.get()
                    if not self.action_list:
                        continue
                    finished = self.action_list.pop(0)
                    assert isinstance(
                        finished, Finished
                    ), f"Matcher finished while running handler {handler} but got {finished}"
                    assert (
                        not self.action_list
                    ), f"Unexpected models {self.action_list}, expected empty after finished"
                    break


class ProcessMixin(BaseApp):
    def test_matcher(self, matcher: Type["Matcher"]) -> MatcherContext:
        return MatcherContext(self, matcher)
