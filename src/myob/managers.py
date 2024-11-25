import re
import requests
from datetime import date
from typing import Any

from .constants import DEFAULT_PAGE_SIZE, MYOB_BASE_URL
from .credentials import PartnerCredentials
from .endpoints import ALL, CRUD, GET, METHOD_MAPPING, METHOD_ORDER, POST, PUT, Method
from .exceptions import (
    MyobBadRequest,
    MyobConflict,
    MyobExceptionUnknown,
    MyobForbidden,
    MyobGatewayTimeout,
    MyobInternalServerError,
    MyobNotFound,
    MyobRateLimitExceeded,
    MyobUnauthorized,
)
from .types import MethodDetails


class Manager:
    def __init__(
        self,
        name: str,
        credentials: PartnerCredentials,
        company_id: str | None = None,
        endpoints: list = [],  # noqa: B006
        raw_endpoints: list = [],  # noqa: B006
    ) -> None:
        self.credentials = credentials
        self.name = "_".join(p for p in name.rstrip("/").split("/") if "[" not in p)
        self.base_url = MYOB_BASE_URL
        if company_id is not None:
            self.base_url += company_id + "/"
        if name:
            self.base_url += name
        self.method_details: dict[str, MethodDetails] = {}
        self.company_id = company_id

        # Build ORM methods from given url endpoints.
        for method, base, name in endpoints:
            if method == CRUD:
                for m in METHOD_ORDER:
                    self.build_method(
                        m,
                        METHOD_MAPPING[m]["endpoint"](base),
                        METHOD_MAPPING[m]["hint"](name),
                    )
            else:
                self.build_method(
                    method,
                    METHOD_MAPPING[method]["endpoint"](base),
                    METHOD_MAPPING[method]["hint"](name),
                )
        # Build raw methods (ones where we don't want to tinker with the endpoint or hint)
        for method, endpoint, hint in raw_endpoints:
            self.build_method(method, endpoint, hint)

    def build_method(self, method: Method, endpoint: str, hint: str) -> None:
        full_endpoint = self.base_url + endpoint
        url_keys = re.findall(r"\[([^\]]*)\]", full_endpoint)
        template = full_endpoint.replace("[", "{").replace("]", "}")

        required_kwargs = url_keys.copy()
        if method in (PUT, POST):
            required_kwargs.append("data")

        def inner(*args: Any, timeout: int | None = None, **kwargs: Any) -> str | dict:
            if args:
                raise AttributeError("Unnamed args provided. Only keyword args accepted.")

            # Ensure all required url kwargs have been provided.
            missing_kwargs = set(required_kwargs) - set(kwargs.keys())
            if missing_kwargs:
                raise KeyError(
                    f"Missing kwargs {list(missing_kwargs)}. Endpoint requires {required_kwargs}."
                )

            # Parse kwargs.
            url_kwargs = {}
            request_kwargs_raw = {}
            for k, v in kwargs.items():
                if k in url_keys:
                    url_kwargs[k] = v
                elif k != "data":
                    request_kwargs_raw[k] = v

            # Determine request method.
            request_method = GET if method == ALL else method

            # Build url.
            url = template.format(**url_kwargs)

            # Build request kwargs (header/query/body)
            request_kwargs = self.build_request_kwargs(
                request_method, data=kwargs.get("data"), **request_kwargs_raw
            )
            response = requests.request(request_method, url, timeout=timeout, **request_kwargs)

            if response.status_code == 200:
                # We don't want to be deserialising binary responses..
                if not response.headers.get("content-type", "").startswith("application/json"):
                    return response.content

                try:
                    return response.json()
                except ValueError:
                    # Handle possible empty string response to DELETE request
                    if method == "DELETE" and response.content == b"":
                        return {}
                    raise
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                raise MyobBadRequest(response)
            elif response.status_code == 401:
                raise MyobUnauthorized(response)
            elif response.status_code == 403:
                if response.json()["Errors"][0]["Name"] == "RateLimitError":
                    raise MyobRateLimitExceeded(response)
                raise MyobForbidden(response)
            elif response.status_code == 404:
                raise MyobNotFound(response)
            elif response.status_code == 409:
                raise MyobConflict(response)
            elif response.status_code == 500:
                raise MyobInternalServerError(response)
            elif response.status_code == 504:
                raise MyobGatewayTimeout(response)
            else:
                raise MyobExceptionUnknown(response)

        # Build method name
        method_name = "_".join(p for p in endpoint.rstrip("/").split("/") if "[" not in p).lower()
        # If it has no name, use method.
        if not method_name:
            method_name = method.lower()
        # If it already exists, prepend with method to disambiguate.
        elif hasattr(self, method_name):
            method_name = f"{method.lower()}_{method_name}"
        self.method_details[method_name] = MethodDetails(
            kwargs=required_kwargs,
            hint=hint,
        )
        setattr(self, method_name, inner)

    def build_request_kwargs(self, method: Method, data: dict | None = None, **kwargs: Any) -> dict:
        request_kwargs = {}

        # Build headers.
        request_kwargs["headers"] = {
            "Authorization": f"Bearer {self.credentials.oauth_token}",
            "x-myobapi-key": self.credentials.consumer_key,
            "x-myobapi-version": "v2",
        }
        if self.company_id:
            try:
                # Try to look up credentials for the companyfile if they've been set up. Else,
                # pass through silently, as the user is likely to have been set up with SSO,
                # in which case the credentials are not required.
                companyfile_credentials = self.credentials.companyfile_credentials[self.company_id]
                request_kwargs["headers"].update(
                    {
                        "x-myobapi-cftoken": companyfile_credentials,
                    }
                )
            except KeyError:
                pass

        if "headers" in kwargs:
            request_kwargs["headers"].update(kwargs["headers"])

        # Build query.
        request_kwargs["params"] = {}
        filters = []

        def build_value(value: Any) -> str:
            if issubclass(type(value), date):
                return f"datetime'{value}'"
            if isinstance(value, bool):
                return str(value).lower()
            return f"'{value}'"

        if "raw_filter" in kwargs:
            filters.append(kwargs["raw_filter"])

        for k, v in kwargs.items():
            if k not in [
                "orderby",
                "format",
                "headers",
                "page",
                "limit",
                "templatename",
                "timeout",
                "raw_filter",
            ]:
                operator = "eq"
                for op in ["lt", "gt"]:
                    if k.endswith(f"__{op}"):
                        k = k[:-4]
                        operator = op
                if not isinstance(v, list | tuple):
                    v = [v]
                filters.append(" or ".join(f"{k} {operator} {build_value(v_)}" for v_ in v))

        if filters:
            request_kwargs["params"]["$filter"] = " and ".join(f"({f})" for f in filters)

        if "orderby" in kwargs:
            request_kwargs["params"]["$orderby"] = kwargs["orderby"]

        page_size = DEFAULT_PAGE_SIZE
        if "limit" in kwargs:
            page_size = int(kwargs["limit"])
            request_kwargs["params"]["$top"] = page_size  # type: ignore[assignment]

        if "page" in kwargs:
            request_kwargs["params"]["$skip"] = (int(kwargs["page"]) - 1) * page_size  # type: ignore[assignment]

        if "format" in kwargs:
            request_kwargs["params"]["format"] = kwargs["format"]

        if "templatename" in kwargs:
            request_kwargs["params"]["templatename"] = kwargs["templatename"]

        if method in ("PUT", "POST"):
            request_kwargs["params"]["returnBody"] = "true"

        # Build body.
        if data is not None:
            request_kwargs["json"] = data

        return request_kwargs

    def __repr__(self) -> str:
        def _get_signature(name: str, kwargs: list[str]) -> str:
            return f"{name}({', '.join(kwargs)})"

        def _print_method(name: str, kwargs: list[str], hint: str, offset: int) -> str:
            return f"{_get_signature(name, kwargs):>{offset}} - {hint}"

        offset = max(len(_get_signature(k, v["kwargs"])) for k, v in self.method_details.items())
        options = "\n    ".join(
            _print_method(k, v["kwargs"], v["hint"], offset)
            for k, v in sorted(self.method_details.items())
        )
        return f"{self.name}{self.__class__.__name__}:\n    {options}"
