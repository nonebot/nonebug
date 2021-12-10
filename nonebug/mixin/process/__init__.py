from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, List, Type, Optional

from nonebug.base import BaseApp

from ..call_api import ApiContext
from .model import Model, Paused, Finished, Rejected, ReceiveEvent

if TYPE_CHECKING:
    from nonebot.typing import T_State
    from nonebot.matcher import Matcher
    from nonebot.adapters import Bot, Event


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
        async with stack:
            while self.action_list:
                try:
                    receive_event = self.action_list.pop(0)
                    assert isinstance(
                        receive_event, ReceiveEvent
                    ), f"Unexpected model {receive_event} expected ReceiveEvent"
                    assert (
                        self.matcher.handlers
                    ), f"Matcher has no handler remain, but received event {receive_event}"
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


class ProcessMixin(BaseApp):
    def test_matcher(self, matcher: Type["Matcher"]) -> MatcherContext:
        return MatcherContext(self, matcher)
