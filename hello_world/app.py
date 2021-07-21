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
    user_id = 1
    print(user_id)
    if user_id is None:
        return httpUtil.response({""}, 400, "PUT, OPTIONS")

    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id FROM dating_profile WHERE user_id = %s", (user_id,))
    date_profile = dict(cur.fetchone())

    if date_profile is None:
        return httpUtil.response({""}, 400, "PUT, OPTIONS")

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE FROM dating_interested_in WHERE dating_profile_id = %s", (date_profile.get('id'),))

    parameters = json.loads(event['body'])
    interested_in = parameters.get('interested_in')
    print(interested_in)
    for v in interested_in:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("INSERT INTO dating_interested_in (dating_profile_id, interested_in_gender) VALUES (%s, %s)",
                    (date_profile.get('id'), v,))

    return httpUtil.response(json.dumps({}), 200, "PUT, OPTIONS")


def get_match_list(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    # FIXME: Set JWT Tokens
    uid = 1
    conn = postgres.connection()
    cur = conn.cursor()
    cur.execute("SELECT dii.id FROM dating_interested_in dii "
                "INNER JOIN dating_profile dp on dii.dating_profile_id = dp.id "
                "INNER JOIN accounts a on dp.user_id = a.id "
                "WHERE a.id = %s;", uid)
    interested_in = cur.fetchall()

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT up.*, ug.image_url, m_p.id, m_m.id "
                "FROM user_profile as up "
                
                "INNER JOIN accounts as a on up.account_id = a.id "
                "LEFT JOIN user_gallery as ug ON up.id = ug.user_id and ug.is_main IS TRUE "
                "INNER JOIN dating_profile as dp ON a.id = dp.user_id "
                "LEFT JOIN match as m_p on a.id = m_p.user_plus AND m_p.user_minus = %s "
                "LEFT JOIN match as m_m on a.id = m_m.user_minus and m_m.user_plus = %s "
                # Dating Gender Match
                "WHERE dp.gender_id IN %s "
                "AND m_p.id IS NULL", (uid, uid, tuple(interested_in),))

    profile_dict = cur.fetchall()
    return httpUtil.response(json.dumps({"profiles": profile_dict}, default=str), 200, "GET, OPTIONS")


def match(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    uid = 1
    uuid = event['interested_in_id']
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO match (user_plus, user_minus, status) "
                "VALUES (%s, %s, 1)",
                (uid, uuid))
    return httpUtil.response(json.dumps({}), 200, "POST, OPTIONS")


def match_list(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    uid = 1
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM match as m where user_plus = %s and status = 1", uid)
    liked_matched_list = cur.fetchall()
    matched_list = []
    for k,v in liked_matched_list:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM match as m where user_minus = %s and user_plus = %s and status = 1", uid, v.id)
        receive_matched_list = cur.fetchall()
        for k,v in receive_matched_list:
            matched_list.append(v)

    return httpUtil.response(json.dumps({'matched': matched_list}), 200, "GET, OPTIONS")


def chat(event, context):
    uid = 1
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO chat "
                "(user_send, user_receive, message, message_type) "
                "VALUES "
                "(%s, %s, %s, %s)", (uid, 1, "ddd", 1))
    return
