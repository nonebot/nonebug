from typing import TYPE_CHECKING

from nonebot.matcher import Matcher

if TYPE_CHECKING:
    from . import MatcherContext


def make_fake_matcher(ctx: "MatcherContext"):
    # FIXME: no super available
    class FakeMatcher(Matcher):
        @classmethod
        async def check_perm(cls, *args, **kwargs) -> bool:
            result = await super().check_perm(*args, **kwargs)
            return ctx.got_check_rule(cls, result)

        @classmethod
        async def check_rule(cls, *args, **kwargs) -> bool:
            result = await super().check_rule(*args, **kwargs)
            return ctx.got_check_permission(cls, result)

    return FakeMatcher
