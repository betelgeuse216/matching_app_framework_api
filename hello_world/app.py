import base64
import json
import psycopg2
import psycopg2.extras
# import requests
import database.postgres as postgres


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    return {
        "statusCode": 200,
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }


def get_account(event, context):
    conn = postgres.connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts")
    rows = cur.fetchall()

    # TODO implement
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"

        },
        'body': json.dumps({"accounts": rows}, default=str)
    }


def test_json(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        'body': '{"page":2,"per_page":6,"total":12,"total_pages":2,"data":[{"id":7,"email":"michael.lawson@reqres.in","first_name":"Michael","last_name":"Lawson","avatar":"https://reqres.in/img/faces/7-image.jpg"},{"id":8,"email":"lindsay.ferguson@reqres.in","first_name":"Lindsay","last_name":"Ferguson","avatar":"https://reqres.in/img/faces/8-image.jpg"},{"id":9,"email":"tobias.funke@reqres.in","first_name":"Tobias","last_name":"Funke","avatar":"https://reqres.in/img/faces/9-image.jpg"},{"id":10,"email":"byron.fields@reqres.in","first_name":"Byron","last_name":"Fields","avatar":"https://reqres.in/img/faces/10-image.jpg"},{"id":11,"email":"george.edwards@reqres.in","first_name":"George","last_name":"Edwards","avatar":"https://reqres.in/img/faces/11-image.jpg"},{"id":12,"email":"rachel.howell@reqres.in","first_name":"Rachel","last_name":"Howell","avatar":"https://reqres.in/img/faces/12-image.jpg"}],"support":{"url":"https://reqres.in/#support-heading","text":"To keep ReqRes free, contributions towards server costs are appreciated!"}}'
    }


def get_profile_list(event, context):
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT up.*, ug.image_url "
                "FROM user_profile as up "
                "LEFT JOIN user_gallery as ug ON up.id = ug.user_id "
                "and ug.is_main IS TRUE")
    profile_dict = cur.fetchall()
    return {
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        'statusCode': 200,
        'body': json.dumps({"profiles": profile_dict}, default=str)
    }


def get_profile(event, context):
    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    parameters = event.get('pathParameters')
    ids = parameters.get('id')
    cur.execute("SELECT * FROM user_profile where id = %s", (ids,))
    profile_dict = dict(cur.fetchone())
    return {
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        'statusCode': 200,
        'body': json.dumps({"profile": profile_dict}, default=str)
    }


def get_images_all(event, context):
    conn = postgres.connection()
    parameters = event.get('pathParameters')
    profile_id = parameters.get('id')
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM user_gallery where user_id = %s", (profile_id,))
    images = cur.fetchall()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        'body': json.dumps({"images": images}, default=str)
    }


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
        return {"statusCode": 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Accept-Charset': 'UTF-8',
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                    "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
                    "Access-Control-Allow-Methods": "GET, OPTIONS"
                },
                "body": json.dumps({
                    "message": "hello world",
                    # "location": ip.text.replace("\n", "")
                })
                }

    conn = postgres.connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id FROM dating_profile WHERE user_id = %s", (user_id,))
    date_profile = dict(cur.fetchone())

    if date_profile is None:
        return {"statusCode": 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Accept-Charset': 'UTF-8',
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                    "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
                    "Access-Control-Allow-Methods": "GET, OPTIONS"
                },
                "body": json.dumps({
                    "message": "hello world",
                    # "location": ip.text.replace("\n", "")
                })
                }

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE dating_profile_id WHERE dating_profile_id = %s", (date_profile.get('id'),))

    parameters = json.load(event.get('event'))
    interested_in = parameters.get('interested_in')

    for k, v in interested_in:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("INSERT dating_profile_id (dating_profile_id, interested_in_gender) VALUES (%s, %s)",
                    (date_profile.get('id'), v,))

    return {"statusCode": 200,
            'headers': {
                'Content-Type': 'application/json',
                'Accept-Charset': 'UTF-8',
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "Origin,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,locale",
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            },
            "body": json.dumps({
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            })
            }
