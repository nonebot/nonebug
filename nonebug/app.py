from .mixin import CallApiMixin, ProcessMixin, DependentMixin


class ProcessorApp(DependentMixin, CallApiMixin, ProcessMixin):
    ...


class App(ProcessorApp):
    ...
