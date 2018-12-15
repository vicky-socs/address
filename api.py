import copy
from datetime import datetime
from http import HTTPStatus

from bson import ObjectId
from bson.json_util import dumps
from eve import Eve
from eve_swagger import add_documentation, swagger
from flask import request, Request, Response
from gevent.pywsgi import WSGIServer

from custom_library.custom_http_manager import manager
from helper import (
    fetch_pincode_data, get_request_data, get_response_data,
    sanitize_data, ZylaValidator
)
from logger import get_logger, get_sentry_handler
from schema import custom_paths
from settings import (
    DEBUG, LOG_LEVEL, redis_conn, RELEASE_VERSION
)


app = Eve(redis=redis_conn, validator=ZylaValidator)
app.register_blueprint(swagger)


@app.route("/api/v1/address/schema")
def address_schema():
    schema_response = manager.request(
        method="GET", url="http://localhost:5000/api-docs")
    return schema_response.data, schema_response.status


@app.before_request
def log_every_request() -> None:
    """

    :param resource:
    :param request:
    :param response:
    :return:
    """
    # set logger
    app.logger = get_logger("chat_service", level=LOG_LEVEL)
    app.logger.addHandler(get_sentry_handler(release=RELEASE_VERSION))
    # logger done
    headers, url, method, payload, args = get_request_data(request)
    app.logger.info("Request url: " + url)
    app.logger.info("Request headers: " + headers)
    app.logger.info("Request method: " + method)
    app.logger.info("Request args: " + args)
    app.logger.info("Request body: " + payload)
    return


@app.after_request
def log_every_response(response):
    status, status_code = get_response_data(response=response)
    app.logger.info("Response status: " + str(status))
    app.logger.handlers = []
    return response


def load_pincode_data():
    pincode_version_data = app.data.find("pincode_version",
                                         None, None).sort("_created", -1)
    data_count = pincode_version_data.count()
    if data_count:
        pincode_version_data = pincode_version_data[0]
        pincode_version = pincode_version_data.get("version")
        pincode_data, insert = fetch_pincode_data(
            pincode_version=pincode_version,
            verify_checksum=True)
    else:
        pincode_data, insert = fetch_pincode_data()
    if insert:
        version_payload = {
            "version": pincode_data,
            "_created": datetime.utcnow()
        }
        app.data.insert("pincode_version", version_payload)


def update_address_on_post(items):
    if isinstance(items, list):
        for item in items:
            update_address_on_post(item)
    if isinstance(items, dict):
        payload = copy.deepcopy(items)
        payload_key = "patientId"
        payload_data = {}
        for k, v in payload.items():
            if k == payload_key:
                data = {k: v}
                payload_data.update(data)
        patient_address = app.data.find_one("patient_address", None,
                                            False, False, **payload_data)
        if patient_address:
            address_id = patient_address.get("_id")
            payload.pop("patientId")
            app.data.update("patient_address", address_id,
                            payload, patient_address)
            response_data = app.data.find_one("patient_address", None,
                                              False, False, **payload_data)
            return response_data


def get_create_data(request: Request, response: Response):
    resource_name, type_ = request.endpoint.split("|")
    if type_ == "resource":
        response_data = response.json
        resource_id = response_data.get("_id")
        payload = {
            "_id": ObjectId(resource_id)
        }
        resource_data = app.data.find_one(resource_name, None,
                                          False, False, **payload)
        return resource_data, HTTPStatus.CREATED


def update_address_on_post_callback(request: Request, response: Response):
    response_data = response.json
    issues = response_data.get("issues")
    if issues:
        if "patientId" in list(issues.keys()):
            items = request.json
            updated = update_address_on_post(items=items)
            response.data = dumps(sanitize_data(updated))
            response.status_code = HTTPStatus.OK
    else:
        if response.status_code == HTTPStatus.CREATED:
            response_data, status_code = get_create_data(request=request,
                                                         response=response)
            response.data = dumps(sanitize_data(response_data))


add_documentation(custom_paths)

app.on_post_POST_patient_address = update_address_on_post_callback

if __name__ == "__main__":
    with app.app_context():
        load_pincode_data()
    if DEBUG:
        try:
            app.run(host="0.0.0.0", port=5000, debug=True)
        except KeyboardInterrupt:
            app.logger.info("Exiting service")
    else:
        try:
            http_server = WSGIServer(('0.0.0.0', 5000), application=app,
                                     backlog=1000, spawn=10)
            http_server.serve_forever()
        except KeyboardInterrupt as e:
            app.logger.info("Exiting Service")
        except Exception as e:
            app.logger.info("Exiting Service")
