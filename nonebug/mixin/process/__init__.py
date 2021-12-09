from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Type, Optional

from nonebug.base import BaseApp

from ..call_api import ApiContext

if TYPE_CHECKING:
    from nonebot.typing import T_State
    from nonebot.matcher import Matcher
    from nonebot.adapters import Bot, Event


class MatcherContext(ApiContext):
    def __init__(self, app: "ProcessMixin", matcher: Type["Matcher"], *args, **kwargs):
        super(MatcherContext, self).__init__(app, *args, **kwargs)
        self.matcher_class = matcher
        # TODO
        self.bot: Optional[Bot] = None
        self.event: Optional[Event] = None
        self.state: T_State = {}

    def receive_event(
        self, bot: "Bot", event: "Event", state: Optional["T_State"] = None
    ) -> None:
        # TODO
        self.bot = bot
        self.event = event
        if state:
            self.state = state

    def should_paused(self):
        ...

    def should_rejected(self):
        ...

    async def run_test(self):
        assert (
            self.bot and self.event
        ), "Bot and Event should be set. Use `ctx.pass_params` to set them."
        try:
            matcher = self.matcher_class()
        except:
            ...


class ProcessMixin(BaseApp):
    def test_matcher(self, matcher: Type["Matcher"]) -> MatcherContext:
        return MatcherContext(self, matcher)
