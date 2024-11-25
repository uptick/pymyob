from requests import Response


class MyobException(Exception):  # noqa: N818
    def __init__(self, response: Response, msg: str | None = None) -> None:
        self.response = response
        try:
            self.errors = response.json()["Errors"]
            e = self.errors[0]
            name, message, details = (
                e["Name"],
                e["Message"] or "",
                e["AdditionalDetails"],
            )
            self.problem = f"{name}: {message} {details}"
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


class MyobRateLimitExceeded(MyobForbidden):
    # HTTP 403: Forbidden, with response.json()['Errors'][0]['Name'] == 'RateLimitError'
    pass


class MyobNotFound(MyobException):
    # HTTP 404: Not Found
    pass


class MyobConflict(MyobException):
    # HTTP 409: Conflict
    pass


class MyobInternalServerError(MyobException):
    # HTTP 500: Internal Server Error
    pass


class MyobGatewayTimeout(MyobException):
    # HTTP 504: Gateway Timeout
    pass


class MyobExceptionUnknown(MyobException):
    # Any other exception.
    pass
