class MyobException(Exception):
    def __init__(self, response, msg=None):
        self.response = response
        try:
            self.errors = response.json()['Errors']
            e = self.errors[0]
            self.problem = '%s: %s %s' % (e['Name'], e['Message'] or '', e['AdditionalDetails'])
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


class MyobForbidden(MyobException):
    # HTTP 403: Forbidden
    pass


class MyobNotFound(MyobException):
    # HTTP 404: Not Found
    pass


class MyobExceptionUnknown(MyobException):
    # Any other exception.
    pass
