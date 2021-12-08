from .mixin import CallApiMixin, HandlerMixin


class ProcessorApp(HandlerMixin, CallApiMixin):
    ...


class App(ProcessorApp):
    ...
