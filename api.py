import requests
from eve import Eve
from eve_swagger import swagger, add_documentation
from flask import request
from gevent.pywsgi import WSGIServer
from datetime import datetime

from helper import ZylaValidator, get_response_data, get_request_data, fetch_pincode_data
from logger import get_logger, get_sentry_handler
from schema import custom_paths
from settings import LOG_LEVEL, RELEASE_VERSION
from settings import redis_conn, DEBUG

app = Eve(redis=redis_conn, validator=ZylaValidator)
app.register_blueprint(swagger)


@app.route("/api/v1/address/schema")
def address_schema():
    schema_response = requests.get("http://localhost:5000/api-docs")
    return schema_response.text, schema_response.status_code


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
    pincode_version_data = app.data.find("pincode_version", None, None).sort("_created", -1)
    data_count = pincode_version_data.count()
    if data_count:
        pincode_version_data = pincode_version_data[0]
        pincode_version = pincode_version_data.get("version")
        pincode_data, insert = fetch_pincode_data(pincode_version=pincode_version, verify_checksum=True)
    else:
        pincode_data, insert = fetch_pincode_data()
    if insert:
        version_payload = {
            "version": pincode_data,
            "_created": datetime.utcnow()
        }
        app.data.insert("pincode_version", version_payload)


add_documentation(custom_paths)

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
            http_server = WSGIServer(('0.0.0.0', 5000), application=app, backlog=256)
            http_server.serve_forever()
        except KeyboardInterrupt as e:
            app.logger.info("Exiting Service")
        except Exception as e:
            app.logger.info("Exiting Service")
