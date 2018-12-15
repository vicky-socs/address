import urllib3
from urllib3.poolmanager import PoolManager

from settings import ZYLA_SERVICE_KEY


service_headers = {
    "client": "service",
    "access_token": ZYLA_SERVICE_KEY,
    "Content-Type": "application/json"
}
manager = PoolManager(10, headers=service_headers)
urllib3.disable_warnings()
