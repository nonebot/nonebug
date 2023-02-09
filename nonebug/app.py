from .mixin import DriverMixin, CallApiMixin, ProcessMixin, DependentMixin


class App(DependentMixin, CallApiMixin, ProcessMixin, DriverMixin):
    ...
