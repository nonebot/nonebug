from .mixin import DriverMixin, CallApiMixin, ProcessMixin, DependentMixin


class ProcessorApp(DependentMixin, CallApiMixin, ProcessMixin):
    ...


class App(ProcessorApp, DriverMixin):
    ...
