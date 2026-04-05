import re


DEFAULT_LIMIT = 10
MAX_LIMIT = 100

CREATED = "created successfully."
UPDATED = "updated successfully."
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
    "our_offer",
    "owner",
    "make",
    "model",
}
OPTIONAL_IMPORT_FIELDS = {
    "alternate_mobile",
    "client_offer",
    "variant",
    "color",
    "telecaller",
    "executive",
    "address",
    "state",
    "city",
    "area",
    "pincode",
}
MOBILE_PATTERN = re.compile(r"^(0|9)\d{9}$")
YEAR_PATTERN = re.compile(r"^\d{4}$")
PINCODE_PATTERN = re.compile(r"^\d{6}$")

BUY_LEAD_IMPORT_FILE_TYPE = "import buy lead"
BUY_LEAD_ERROR_FILE_TYPE = "error buy lead"
