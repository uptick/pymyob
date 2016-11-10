

class MyobException(Exception):
    def __init__(self, response, msg=None):
        self.response = response
        super().__init__(msg)


class MyobUnauthorized(MyobException):
    # HTTP 401: Unauthorized
    def __init__(self, response):
        self.errors = response.json()['Errors']
        self.problem = self.errors[0]['Message']
        super().__init__(response, self.problem)


class MyobExceptionUnknown(MyobException):
    # Any other exception.
    pass
