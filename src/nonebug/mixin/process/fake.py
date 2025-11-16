from collections.abc import Awaitable
from typing_extensions import ParamSpec
from typing import TYPE_CHECKING
from collections.abc import Callable

from _pytest.outcomes import OutcomeException

from .model import Error

if TYPE_CHECKING:
    from nonebot.matcher import Matcher

    from . import MatcherContext

P = ParamSpec("P")


def make_fake_default_state(ctx: "MatcherContext", matcher: type["Matcher"]) -> dict:
    return {**matcher._default_state, "__nonebug_matcher__": matcher}


def make_fake_check_perm(
    ctx: "MatcherContext", matcher: type["Matcher"]
) -> Callable[..., Awaitable[bool]]:
    check_perm = matcher.__dict__["check_perm"]

    @classmethod
    async def fake_check_perm(cls: type["Matcher"], *args, **kwargs) -> bool:
        result = await check_perm.__get__(None, cls)(*args, **kwargs)
        return ctx.got_check_permission(
            cls._default_state["__nonebug_matcher__"], result
        )

    return fake_check_perm


def make_fake_check_rule(
    ctx: "MatcherContext", matcher: type["Matcher"]
) -> Callable[..., Awaitable[bool]]:
    check_rule = matcher.__dict__["check_rule"]

    @classmethod
    async def fake_check_rule(cls: type["Matcher"], *args, **kwargs) -> bool:
        result = await check_rule.__get__(None, cls)(*args, **kwargs)
        return ctx.got_check_rule(cls._default_state["__nonebug_matcher__"], result)

    return fake_check_rule


def make_fake_simple_run(
    ctx: "MatcherContext", matcher: type["Matcher"]
) -> Callable[..., Awaitable[None]]:
    simple_run = matcher.simple_run

    async def fake_simple_run(self: "Matcher", *args, **kwargs) -> None:
        from nonebot.exception import (
            PausedException,
            FinishedException,
            RejectedException,
        )

        try:
            await simple_run(self, *args, **kwargs)
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


def make_fake_run(
    ctx: "MatcherContext", matcher: type["Matcher"]
) -> Callable[..., Awaitable[None]]:
    run = matcher.run

    async def fake_run(self: "Matcher", *args, **kwargs) -> None:
        try:
            await run(self, *args, **kwargs)
        except (Exception, OutcomeException) as e:
            ctx.errors.append(Error(self.__class__, e))
            raise

    return fake_run


PATCHES = {
    "check_perm": make_fake_check_perm,
    "check_rule": make_fake_check_rule,
    "simple_run": make_fake_simple_run,
    "run": make_fake_run,
}
