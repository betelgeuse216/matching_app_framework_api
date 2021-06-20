import base64
import json
import psycopg2
import psycopg2.extras
# import requests
import database.postgres as postgres

# """Sample pure Lambda function
#
# Parameters
# ----------
# event: dict, required
#     API Gateway Lambda Proxy Input Format
#
# Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
#
# context: object, required
#     Lambda Context runtime methods and attributes
#
#     Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
#
# Returns
# ------
# API Gateway Lambda Proxy Output Format: dict
#
#     Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
# """
from util import httpUtil


def get_account(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    conn = postgres.connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts")
    rows = cur.fetchall()

    # TODO implement
    return httpUtil.response(json.dumps({"accounts": rows}, default=str), 200, "GET, OPTIONS")


def get_profile_list(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT up.*, ug.image_url "
                "FROM user_profile as up "
                "LEFT JOIN user_gallery as ug ON up.id = ug.user_id "
                "and ug.is_main IS TRUE")
    profile_dict = cur.fetchall()
    return httpUtil.response(json.dumps({"profiles": profile_dict}, default=str), 200, "GET, OPTIONS")


def get_profile(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    parameters = event.get('pathParameters')
    ids = parameters.get('id')
    cur.execute("SELECT * FROM user_profile where id = %s", (ids,))
    profile_dict = dict(cur.fetchone())
    return httpUtil.response(json.dumps({"profile": profile_dict}, default=str), 200, "GET, OPTIONS")


def get_images_all(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    conn = postgres.connection()
    parameters = event.get('pathParameters')
    profile_id = parameters.get('id')
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM user_gallery where user_id = %s", (profile_id,))
    images = cur.fetchall()
    return httpUtil.response(json.dumps({"images": images}, default=str), 200, "GET, OPTIONS")


def set_gender_interested_in(event, context):
    """
    :param event:
    :param context:
    :return:
    """

    # FIXME: Better way of authenticating?
    # FIXME: Set JWT Tokens
    user_id = event['Authorization']
    print(user_id)
    if user_id is None:
        return httpUtil.response({""}, 400, "POST, OPTIONS")

    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id FROM dating_profile WHERE user_id = %s", (user_id,))
    date_profile = dict(cur.fetchone())

    if date_profile is None:
        return httpUtil.response({""}, 400, "POST, OPTIONS")

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE dating_profile_id WHERE dating_profile_id = %s", (date_profile.get('id'),))

    parameters = json.load(event.get('event'))
    interested_in = parameters.get('interested_in')

    for k, v in interested_in:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("INSERT dating_profile_id (dating_profile_id, interested_in_gender) VALUES (%s, %s)",
                    (date_profile.get('id'), v,))

    return httpUtil.response({""}, 200, "POST, OPTIONS")

def match_time(event, context):
    """

    :param event:
    :param context:
    :return:
    """
