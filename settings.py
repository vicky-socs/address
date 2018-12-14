import logging
import os

from redis import StrictRedis

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "addressService")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", None)
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", None)
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
MONGO_REPLICA_SET = os.getenv("MONGO_REPLICA_SET", None)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "3"))
REDIS_CONN_POOL = int(os.getenv("REDIS_CONN_POOL", "10"))
API_VERSION = os.getenv("API_VERSION", "v1")
DEBUG = bool(int(os.getenv("FLASK_DEBUG", "0")))
LOG_LEVEL = logging.INFO
if DEBUG:
    LOG_LEVEL = logging.DEBUG
API_VERSION = os.getenv("API_VERSION", "v1")
BASE_VERSION = os.getenv("BASE_VERSION", "1")
APP_VERSION = os.getenv("APP_VERSION", "1")
RELEASE_VERSION = BASE_VERSION + ":" + APP_VERSION
SENTRY_DSN = os.getenv("SENTRY_DSN")
SWAGGER_HOST = os.getenv("SWAGGER_HOST", "localhost")
SWAGGER_INFO = {
    'title': 'Patient Address API',
    'version': APP_VERSION,
    'description': 'an API description',
    'termsOfService': 'https://example.com',
    'contact': {
        'name': 'Mrigesh Pokhrel',
        'email': 'mrigesh@zyla.in'
    },
    'license': {
        'name': 'Proprietary',
    },
    'schemes': ['https'],
}
ENABLE_HOOK_DESCRIPTION = bool(os.getenv("ENABLE_HOOK_DESCRIPTION", "1"))
PINCODE_BUCKET_NAME = os.getenv("PINCODE_BUCKET_NAME")
PINCODE_FILENAME = os.getenv("PINCODE_FILENAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
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

redis_conn = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, connection_pool=REDIS_CONN_POOL)

pincode_schema = {
    "pincode": {
        "type": "integer",
        "required": True,
        "coerce": int
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

pincode_version = {
    "version": {
        "type": "string",
    }
}

address_schema = {
    "line1": {
        "type": "string"
    },
    "line2": {
        "type": "string"
    },
    "line3": {
        "type": "string"
    },
    "patientId": {
        "type": "integer"
    },
    "landmark": {
        "type": "string"
    },
    "district": {
        "type": "string"
    },
    "city": {
        "type": "string"
    },
    "state": {
        "type": "string"
    },
    "pincode": {
        "type": "integer"
    }
}

pincode_resource = {
    "schema": pincode_schema,
    "url": "address/pincode",
    "additional_lookup": {
        "url": 'regex([w]+)',
        "field": "pincode"
    },
    "mongo_indexes": {
        "pincode_index": ([("pincode", 1)], {"background": True})
    },
    "item_methods":["GET","PATCH","PUT"],
    "resource_methods" :["GET","POST"]
}

pincode_version_resource = {
    "schema": pincode_version,
    "internal_resource": True
}

address_resource = {
    "schema": address_schema,
    "url": "address",
    "additional_lookup": {
        "url": 'regex([w]+)',
        "field": "patientId"
    },
    "mongo_indexes": {
        "patient_index": ([("patientId", 1)], {"background": True})
    },
    "item_methods":["GET","PATCH","PUT"],
    "resource_methods" :["GET","POST"],
    "id_field":"patientId"
}

DOMAIN = {
    "pincode": pincode_resource,
    "patient_address": address_resource,
    "pincode_version": pincode_version_resource
}
