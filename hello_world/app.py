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
        'body': json.dumps({"accounts": rows}, default=str)
    }


def get_profile(event, context):
    conn = postgres.connection()
    print(event)
    print(event)
    print(event.get('pathParameters'))
    parameters = event.get('pathParameters')
    print(parameters.get('id'))
    ids = parameters.get('id')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile where id = %s", (ids, ))
    return {
        'statusCode': 200,
        'body': json.dumps({"profile": cur.fetchone()}, default=str)
    }


def get_images_all(event, context):
    conn = postgres.connection()
    parameters = event.get('pathParameters')
    profile_id = parameters.get('id')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM user_gallery where user_id = %s", (profile_id, ))
    images = cur.fetchall()
    base64_images = []
    for image in images:
        image_dict = dict(image)
        print(image_dict)
        image_b64 = None
        print("rip")
        if 'image_data' in image_dict:
            print(image_dict)
            print("convert")
            image_b64 = base64.b64encode(image_dict.get('image_data'))
        else:
            print("no")
        print(image_b64)
        print(image_dict)
        image_dict['image_data'] = image_b64
        base64_images.append(image_dict)

    return {
        'statusCode': 200,
        'body': json.dumps({"images": base64_images}, default=str)
    }