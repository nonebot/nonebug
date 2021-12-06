class ApiOutOfBoundException(Exception):
    def __repr__(self):
        return "ApiOutOfBoundException"


class ApiActionAssertException(Exception):
    def __init__(self, action: str, name: str):
        self.action = action
        self.name = name

    def __repr__(self):
        return f"ApiActionAssertException,expect: {self.action},But get: {self.name}"

    def __str__(self):
        return self.__repr__()


class ApiDataAssertException(Exception):
    def __init__(self, action: str, key: str, expect_data, data):
        self.action = action
        self.key = key
        self.expect_data = expect_data
        self.data = data

    def __repr__(self):
        return f"ApiDataException,API action: {self.action}, key: {self.key} ,\n expect: {self.expect_data},\n But get: {self.data}"

    def __str__(self):
        return self.__repr__()


class ApiTypeAssertException(Exception):
    def __init__(self, action: str, key: str, expect_type, type):
        self.action = action
        self.key = key
        self.expect_type = expect_type
        self.type = type

    def __repr__(self):
        return f"ApiTypeException,API action: {self.action}, key: {self.key} ,\n expect_type: {self.expect_type},\n But get: {self.type}"

    def __str__(self):
        return self.__repr__()