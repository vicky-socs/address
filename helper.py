import csv
import json
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError
from eve.io.mongo import Validator

from logger import get_logger
from settings import PINCODE_BUCKET_NAME, PINCODE_FILENAME, \
    AWS_ACCESS_KEY, AWS_SECRET_KEY

log = get_logger("address_logger")


class ZylaValidator(Validator):
    def _validate_description(self, description, field, value):
        """ {'type': 'string'} """
        # Accept description attribute, used for swagger doc generation
        pass

    def _validate_example(self, example, field, value):
        """ {'type': 'string'}"""
        if example and not isinstance(value, str):
            self._error(field, "Value must be a string")

    def _validate_email(self, email, field, value):
        """ {'type':'string'} """
        if email:
            try:
                validate_email(email=value)
            except EmailNotValidError as e:
                self._error(field, str(e))


def get_response_data(response):
    status = response.status
    status_code = response.status_code
    return status, status_code


def get_request_data(request):
    headers = "[" + str(request.headers).replace("\r\n", "|") + "]"
    method = request.method
    url = request.url
    payload = request.data
    if payload:
        payload = json.dumps(request.json)
    else:
        payload = ""
    args = request.args
    if not len(args):
        args = ""
    else:
        args = json.dumps(args)
    return headers, url, method, payload, args


def insert_pincode_data(payload_data_list, refresh=False):
    """

    :param payload_data_list:
    :param refresh:
    :return:
    """
    from api import app
    with app.app_context():
        if refresh:
            app.data.driver.db.pincode.drop()
        app.data.insert("pincode", payload_data_list)


def update_pincode_db(file_stream=None, refresh=False):
    """

    :param file_stream:
    :param refresh:
    :return:
    """
    data: bytes = file_stream.read()
    csv_data = data.decode(errors="ignore")
    csv_data = csv_data.splitlines(True)
    parsed_data = csv.DictReader(csv_data)
    pincode_len = len(csv_data)
    payload_items = []
    for data in parsed_data:
        pincode = int(data["pincode"])
        district = data["districtname"]
        state = data["statename"]
        line_no = parsed_data.line_num
        payload = {
            "pincode": pincode,
            "state": state,
            "district": district
        }
        payload_items.append(payload)
        if len(payload_items) > 999:
            insert_pincode_data(payload_data_list=payload_items,
                                refresh=refresh)
            refresh = False
            payload_items = []
        if line_no == pincode_len:
            insert_pincode_data(payload_data_list=payload_items,
                                refresh=refresh)
    return True


def get_data_from_s3(s3, tag=False):
    body = None
    if tag:
        md5sum = s3.head_object(
            Bucket=PINCODE_BUCKET_NAME,
            Key=PINCODE_FILENAME
        )["ETag"]
        md5sum = json.loads(md5sum)
    else:
        data = s3.get_object(
            Bucket=PINCODE_BUCKET_NAME,
            Key=PINCODE_FILENAME
        )
        md5sum = json.loads(data.get("ETag", "null"))
        body = data.get("Body")
    return md5sum, body


def fetch_pincode_data(pincode_version=None, verify_checksum=False):
    """

    :param pincode_version:
    :param verify_checksum:
    :return:
    """
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    update = False
    md5sum = None
    if verify_checksum:
        try:
            md5sum, _ = get_data_from_s3(s3=s3, tag=True)
            if md5sum != pincode_version:
                md5sum, body = get_data_from_s3(s3=s3)
                update = update_pincode_db(file_stream=body, refresh=True)
        except ClientError as e:
            md5sum = None
            update = False
            log.error(e)
    else:
        try:
            md5sum, body = get_data_from_s3(s3=s3)
            update = update_pincode_db(file_stream=body)
        except Exception as e:
            log.error(e)
    return md5sum, update


def sanitize_data(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, ObjectId):
                data[k] = str(v)
            if isinstance(v, datetime):
                data[k] = str(v)
            if isinstance(v, list):
                v1 = []
                for d in v:
                    v1.append(sanitize_data(d))
                data[k] = v1
    return data
