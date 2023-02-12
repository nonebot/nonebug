from typing import TYPE_CHECKING, Type, Callable, Awaitable

from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.exception import PausedException, FinishedException, RejectedException

if TYPE_CHECKING:
    from . import MatcherContext


def make_fake_default_state(ctx: "MatcherContext", matcher: Type[Matcher]) -> dict:
    return {**matcher._default_state, "__nonebug_matcher__": matcher}


def make_fake_check_perm(
    ctx: "MatcherContext", matcher: Type[Matcher]
) -> Callable[..., Awaitable[bool]]:
    check_perm = matcher.__dict__["check_perm"]

    @classmethod
    async def fake_check_perm(cls: Type[Matcher], *args, **kwargs) -> bool:
        result = await check_perm.__get__(None, cls)(*args, **kwargs)
        return ctx.got_check_permission(
            cls._default_state["__nonebug_matcher__"], result
        )

    return fake_check_perm


def make_fake_check_rule(
    ctx: "MatcherContext", matcher: Type[Matcher]
) -> Callable[..., Awaitable[bool]]:
    check_rule = matcher.__dict__["check_rule"]

    @classmethod
    async def fake_check_rule(cls: Type[Matcher], *args, **kwargs) -> bool:
        result = await check_rule.__get__(None, cls)(*args, **kwargs)
        return ctx.got_check_rule(cls._default_state["__nonebug_matcher__"], result)

    return fake_check_rule


def make_fake_simple_run(
    ctx: "MatcherContext", matcher: Type[Matcher]
) -> Callable[..., Awaitable[None]]:
    simple_run = matcher.simple_run

    async def fake_simple_run(
        self: Matcher, bot: Bot, event: Event, state: T_State, *args, **kwargs
    ) -> None:
        try:
            await simple_run(self, bot, event, state, *args, **kwargs)
        except RejectedException:
            ctx.got_action(self._default_state["__nonebug_matcher__"], "reject")
            raise
        except PausedException:
            ctx.got_action(self._default_state["__nonebug_matcher__"], "pause")
            raise
        except FinishedException:
            ctx.got_action(self._default_state["__nonebug_matcher__"], "finish")
            raise

    return fake_simple_run


PATCHES = {
    "check_perm": make_fake_check_perm,
    "check_rule": make_fake_check_rule,
    "simple_run": make_fake_simple_run,
}
