from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from .app import App


# fake class should be created every init
def make_fake_classes():
    from nonebot.drivers import Driver
    from nonebot.typing import overrides
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

    class FakeAdapter(Adapter):
        @overrides(Adapter)
        def __init__(self, driver: Driver, app: "App", **kwargs: Any):
            super(FakeAdapter, self).__init__(driver, **kwargs)
            self.app = app

        @overrides(Adapter)
        def _call_api(self, api: str, **data) -> Any:
            return self.app.got_call_api(api, **data)

    class FakeBot(Bot):
        adapter: FakeAdapter

        @property
        def app(self):
            return self.adapter.app

        @overrides(Bot)
        async def send(
            self,
            event: "Event",
            message: Union[str, "Message", "MessageSegment"],
            **kwargs,
        ) -> Any:
            return self.app.got_call_send(event, message, **kwargs)

    return FakeAdapter, FakeBot
