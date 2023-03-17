import collections
from rest_framework import exceptions
from rest_framework.views import exception_handler

from .logger import logger


def flatten(d, parent_key="", sep="__"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def custom_exception_handler(exc, context):
    """Custom Exception Handler that returns message for end user and errors for developers

    Args:
        exc ([type]): [description]
        context ([type]): [description]

    Returns:
        [type]: [description]
    """
    response = exception_handler(exc, context)
    logger.debug(f"EXE: {exc}")
    logger.exception(exc)

    if isinstance(exc, exceptions.APIException):
        logger.debug("API Error")
        logger.debug(f"Default Detail: {exc.default_detail}")
        logger.debug(f"Error Type: {type(exc)}")
        try:
            if isinstance(exc.detail, list):
                data = {}
                data["errors"] = response.data
                response.data = data
                response.data["message"] = exc.detail[0]
                if isinstance(response.data["message"], exceptions.ErrorDetail):
                    response.data["message"] = str(exc.detail[0])
            elif isinstance(exc.detail, dict):
                data = {}
                data["errors"] = response.data
                response.data = data
                exc.detail = flatten(exc.detail)
                exc_keys = list(exc.detail.keys())
                exc_values = list(exc.detail.values())
                message = {}
                logger.debug(f"Keys: {exc_keys}")
                logger.debug(f"Values: {exc_values}")
                logger.debug(f"Values 0: {exc_values[0]}")
                if len(exc_keys) > 0 and len(exc_values) > 0 and len(exc_values[0]) > 0:
                    message = f"{exc_keys[0]} - {exc_values[0][0]}"
                    if isinstance(exc_values[0], str):
                        message = f"{exc_values[0]}"
                        if exc_values[0] == "Given token not valid for any token type":
                            message = "Token is invalid or expired"
                response.data["message"] = f"{message}"
                logger.debug(f"Message: {message}")
            else:
                response.data["message"] = exc.detail
            if "non_field_errors - " in response.data["message"]:
                response.data["message"] = response.data["message"].replace(
                    "non_field_errors - ", ""
                )
        except Exception as e:
            logger.exception(e)
            response.data["message"] = exc.default_detail

    return response
