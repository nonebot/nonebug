class ApiOutOfBoundException(Exception):
    def __repr__(self):
        return "<ApiOutOfBoundException>"


class ApiActionAssertException(Exception):
    def __init__(self, action: str, name: str):
        self.action = action
        self.name = name

    def __repr__(self):
        return f"<ApiActionAssertException,expect: {self.action},But get: {self.name}>"

    def __str__(self):
        return self.__repr__()


class ApiDataAssertException(Exception):
    def __init__(self, action: str, key: str, expect_data, data):
        self.action = action
        self.key = key
        self.expect_data = expect_data
        self.data = data

    def __repr__(self):
        return f"<ApiDataException,API action: {self.action}, key: {self.key} , expect: {self.expect_data}, But get: {self.data}>"

    def __str__(self):
        return self.__repr__()
