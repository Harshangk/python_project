import re


DEFAULT_LIMIT = 10
MAX_LIMIT = 100

CREATED = "created successfully."
FAILED = "creation failed."
NOTFOUND = "not found."
REMOVED = "remove successfully."
MAXLIMITREACH = "max limit 100 reach."

VALUEERROR = "validation error."
EXCEPTION = "server error."
RECIEVED_REQUEST = "We have received your request."


REQUIRED_IMPORT_FIELDS = {
    "branch",
    "mobile",
    "mode",
    "customer_name",
    "fuel_type",
    "year",
    "kms",
    "owner",
    "make",
    "model",
}
MOBILE_PATTERN = re.compile(r"^(0|9)\d{9}$")
YEAR_PATTERN = re.compile(r"^\d{4}$")