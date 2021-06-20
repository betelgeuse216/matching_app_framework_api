import json


def response(body_message, status_code, allow_methods):
    """
    Response Utils
    :param body_message:
    :param status_code:
    :param allow_methods:
    :return:
    """
    return {
        "statusCode": status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": allow_methods
        },
        "body": body_message
    }
