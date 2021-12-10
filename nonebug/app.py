from .mixin import CallApiMixin, HandlerMixin, ProcessMixin


class ProcessorApp(HandlerMixin, CallApiMixin, ProcessMixin):
    ...


class App(ProcessorApp):
    ...
