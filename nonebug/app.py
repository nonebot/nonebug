from .mixin import CallApiMixin, DependentMixin, DriverMixin, ProcessMixin


class App(DependentMixin, ProcessMixin, CallApiMixin, DriverMixin): ...
