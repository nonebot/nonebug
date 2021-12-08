from .mixin import CallApiMixin, HandlerMixin


class App(HandlerMixin, CallApiMixin):
    ...
