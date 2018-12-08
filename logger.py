import logging
import sys
from logging import INFO, ERROR
from uuid import uuid4

from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from settings import SENTRY_DSN

INFO_FORMAT = "%(asctime)s [ %(name)s::%(levelname)s::%(request_id)s ] %(" \
              "process)d %(message)s"
DEBUG_FORMAT = "%(asctime)s [ %(name)s::%(levelname)s::%(request_id)s ] [ %(" \
               "filename)s:%(lineno)d ] [ %(module)s:%(funcName)s ] %(" \
               "msecs)d %(threadName)s %(process)d %(message)s"


class CustomFilter(logging.Filter):
    """

    """

    def __init__(self, request_id):
        """

        :param request_id:
        """
        self.request_id = request_id

    def filter(self, record):
        """

        :param record:
        :return:
        """
        record.request_id = self.request_id
        return True


def generate_request_id():
    """

    :return:
    """
    request_id = uuid4()
    return str(request_id)


def get_console_handler(formatter):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(filter=CustomFilter(generate_request_id()))
    return console_handler


def get_logger(logger_name, level=INFO):
    logger = logging.getLogger(logger_name)
    if level == INFO:
        formatter = logging.Formatter(INFO_FORMAT)
    else:
        formatter = logging.Formatter(DEBUG_FORMAT)
    logger.setLevel(level)
    handlers = logger.hasHandlers()
    if handlers:
        logger.handlers = []
    logger.addHandler(get_console_handler(formatter=formatter))
    logger.propagate = True
    return logger


def get_sentry_handler(level=ERROR, release=None):
    sentry_dsn = SENTRY_DSN
    sentry_handler = SentryHandler(
        sentry_dsn, release=release
    )
    sentry_handler.setLevel(level)
    setup_logging(sentry_handler)
    return sentry_handler
