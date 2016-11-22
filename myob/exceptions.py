class MyobException(Exception):
    def __init__(self, response, msg=None):
        self.response = response
        try:
            self.errors = response.json()['Errors']
            self.problem = self.errors[0]['Message']
        except Exception:
            self.errors = []
            self.problem = response.reason
        super().__init__(response, self.problem)


class MyobBadRequest(MyobException):
    # HTTP 400: Bad Request
    pass


class MyobUnauthorized(MyobException):
    # HTTP 401: Unauthorized
    pass


class MyobNotFound(MyobException):
    # HTTP 404: Not Found
    pass


class MyobExceptionUnknown(MyobException):
    # Any other exception.
    pass
