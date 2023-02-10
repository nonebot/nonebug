from .mixin import DriverMixin, CallApiMixin, ProcessMixin


class App(CallApiMixin, ProcessMixin, DriverMixin):
    ...
