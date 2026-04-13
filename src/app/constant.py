DEFAULT_LIMIT = 10
MAX_LIMIT = 100
REMARKS = "Imported from CSV"

REQUEST = "received request."
CREATED = "created successfully."
UPDATED = "updated successfully."
FAILED = "creation failed."
NOTFOUND = "not found."
REMOVED = "remove successfully."
MAXLIMITREACH = "max limit 100 reach."

BATCHSIZE = 1000
FILENAME = "file name missing."
FILELARGE = "file too large."
EXTENSION = "only csv allowed."

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
    "year",
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

INVALIDCSV = "Invalid CSV file or missing header."
MISSINGCOLUMNS = "Missing required columns."
MISSINGVALUES = "Missing required columns value."
WRONGVALUES = "Wrong data."
