import logging
import os

MONGODB_HOST = MONGO_HOST = os.getenv("MONGO_HOST")
MONGODB_DB = MONGO_DBNAME = os.getenv("MONGO_DBNAME")
API_VERSION = os.getenv("API_VERSION", "v1")
DEBUG = bool(int(os.getenv("DEBUG", "0")))
LOG_LEVEL = logging.INFO
if DEBUG:
    LOG_LEVEL = logging.DEBUG
MERGE_NESTED_DOCUMENTS = False
URL_PREFIX = "api"
VALIDATE_FILTERS = True
RESOURCE_METHODS = ["GET", "POST", "DELETE"]
ITEM_METHODS = ["GET", "PATCH", "PUT", "DELETE"]
CACHE_CONTROL = "max-age=20; must-revalidate"
ERROR = "error"
ISSUES = "issues"
STATUS = "status"
ITEMS = "items"
META = "meta"
INFO = "api-info"
LINKS = "links"
ETAG = "etag"
DELETED = "deleted"
VERSIONING = False
OPLOG = True
OPLOG_ENDPOINT = "oplog"
OPLOG_RETURN_EXTRA_FIELD = True
SCHEMA_ENDPOINT = "schema"
VALIDATION_ERROR_AS_STRING = True
IF_MATCH = False

pincode_schema = {
    "pincode": {
        "type": "integer",
        "required": True
    },
    "state": {
        "type": "string",
        "required": True
    },
    "district": {
        "type": "string",
        "required": True
    }
}

pincode_resource = {
    "schema": pincode_schema,
    "url": "address/pincode",
    "additional_lookup": {
        "url": 'regex([w]+)',
        "field": "pincode"
    },
    "mongo_indexes":{
        "pincode_index": ([("pincode",1)], {"background": True})
    }
}


DOMAIN = {
    "pincode": pincode_resource
}