from typing import Any

from .credentials import PartnerCredentials
from .endpoints import ENDPOINTS, GET
from .managers import Manager


class Myob:
    """An ORM-like interface to the MYOB API."""

    def __init__(self, credentials: PartnerCredentials) -> None:
        if not isinstance(credentials, PartnerCredentials):
            raise TypeError(f"Expected a Credentials instance, got {type(credentials).__name__}.")
        if credentials.business_id is None:
            raise ValueError(
                "These credentials carry no business_id, so there is nothing to make calls "
                "against. Set it from the `businessId` handed back on the authorisation "
                "redirect."
            )
        self.credentials = credentials
        self._info_manager = Manager(
            "",
            credentials,
            raw_endpoints=[
                (
                    GET,
                    "Info/",
                    "Return API build information for each individual endpoint.",
                ),
            ],
        )
        self._business_manager = Manager(
            "",
            credentials,
            raw_endpoints=[(GET, "", "")],
            business_id=credentials.business_id,
        )
        for endpoint, details in ENDPOINTS.items():
            setattr(
                self,
                details["name"],  # type: ignore[arg-type]
                Manager(
                    endpoint,
                    credentials,
                    endpoints=details["methods"],
                    business_id=credentials.business_id,
                ),
            )

    def business(self) -> dict[str, Any]:
        """Return this business's own details, such as its name and product version.

        Requires `AuthScope.COMPANY_FILE`. MYOB still wraps the response in a `CompanyFile`
        key; callers get the contents.
        """
        return self._business_manager.get()["CompanyFile"]  # type: ignore[attr-defined]

    def info(self) -> str:
        """Return API build information. Not scoped to the business."""
        return self._info_manager.info()  # type: ignore[attr-defined]

    def __repr__(self) -> str:
        names = [*(v["name"] for v in ENDPOINTS.values()), "business", "info"]
        options = "\n    ".join(sorted(names))  # type: ignore[arg-type]
        return f"Myob:\n    {options}"
