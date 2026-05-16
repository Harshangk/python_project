ACCESS_TOKEN_COOKIE_NAME = "accessToken"
REFRESH_TOKEN_COOKIE_NAME = "refreshToken"
ACCESS_TOKEN_COOKIE_PATH = "/"
REFRESH_TOKEN_COOKIE_PATH = "/auth"

PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 42
BOTTOM_MARGIN = 42
LINE_HEIGHT = 14


DEFAULT_LIMIT = 10
MAX_LIMIT = 100
REMARKS = "Imported from CSV"

REQUEST = "received request."
CREATED = "created successfully."
UPDATED = "updated successfully."
FAILED = "creation failed."
NOTFOUND = "not found."
COUNTMISMATCH = "count mismatch."
INVALID = "invalid data."
DUPLICATE = "duplicate data."
REMOVED = "remove successfully."
MAXLIMITREACH = "max limit 100 reach."
INVALIDPAYLOAD = "invalid payload."
EMPTYFILE = "file is empty."

BATCHSIZE = 1000
FILENAME = "file name missing."
FILELARGE = "file too large."
EXTENSION = "only csv allowed."
IMAGEEXTENSION = "only jpg, jpeg, png, webp allowed."
IMAGECONTENTTYPE = "only image/jpeg, image/png, image/jpg, image/webp allowed."

MOBILEERROR = (
    "Mobile number must be between 10 and 15 digits, Mobile must contain only digits."
)

VALUEERROR = "validation error."
EXCEPTION = "server error."

BUYREQUIREDCOLUMS = {
    "branch",
    "mobile",
    "mode",
    "customer_name",
    "make",
    "model",
    "fuel_type",
    "mfg_year",
    "kms",
    "owner",
    "client_offer",
    "our_offer",
}  # noqa

BUYREQUIREDINTCOLUMS = {
    "kms",
    "client_offer",
    "our_offer",
}  # noqa

SOURCEINVALID = "Source required."
BROKERINVALID = "Broker/Dealer required."
INVALIDCSV = "Invalid CSV file or missing header."
MISSINGCOLUMNS = "Missing required columns."
MISSINGVALUES = "Missing required columns value."
WRONGVALUES = "Wrong data."
MISSINGFILES = "Error accessing file from storage."
