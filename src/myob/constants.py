from enum import StrEnum

MYOB_BASE_URL = "https://api.myob.com/accountright/"
MYOB_PARTNER_BASE_URL = "https://secure.myob.com/oauth2/"

AUTHORIZE_URL = "account/authorize/"
ACCESS_TOKEN_URL = "v1/authorize/"  # noqa: S105

DEFAULT_PAGE_SIZE = 400

# Format in which MYOB returns datetimes
# (pymyob won't parse these, but offers the constant for convenience).
DATETIME_FORMATS = ["YYYY-MM-DDTHH:mm:ss", "YYYY-MM-DDTHH:mm:ss.SSS"]


class AuthScope(StrEnum):
    """Granular data scopes accepted by the authorisation endpoint.

    Each scope grants access to one family of endpoints; request only those your
    integration needs. `AuthScope.COMPANY_FILE` is needed by anything that resolves a
    business, so most integrations will want it alongside their data scopes.

    https://developer.myob.com/api/myob-business-api/api-overview/granular_data_scopes/
    """

    BANKING = "sme-banking"
    COMPANY_FILE = "sme-company-file"
    COMPANY_SETTINGS = "sme-company-settings"
    CONTACTS_CUSTOMER = "sme-contacts-customer"
    CONTACTS_EMPLOYEE = "sme-contacts-employee"
    CONTACTS_PERSONAL = "sme-contacts-personal"
    CONTACTS_SUPPLIER = "sme-contacts-supplier"
    GENERAL_LEDGER = "sme-general-ledger"
    INVENTORY = "sme-inventory"
    PAYROLL = "sme-payroll"
    PURCHASES = "sme-purchases"
    SALES = "sme-sales"
    TIMEBILLING = "sme-timebilling"
