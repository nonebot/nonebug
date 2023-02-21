from .mixin import DriverMixin, CallApiMixin, ProcessMixin, DependentMixin


class App(DependentMixin, ProcessMixin, CallApiMixin, DriverMixin):
    ...
