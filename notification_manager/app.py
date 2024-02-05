'''Lambda function that subscribes to the Event Topic
    and sends Request Status messages via email
'''
import json
import os
import boto3

SUCCESS=0


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

    """
    print(json.dumps(event))
    print(context)
    try:
        ses_client = boto3.client("ses")
        CHARSET = "UTF-8"

        for record in event['Records']:
            message=json.loads(record['Sns']['Message'])

            # send a notification email if message is a RequestStatus
            if message['type'] == 'RequestStatus':

                response = ses_client.send_email(
                    Destination={
                        "ToAddresses": [
                            message['requestorEmail'],
                        ],
                    },
                    Message={
                        "Body": {
                            "Text": {
                                "Charset": CHARSET,
                                "Data": message['message'],
                            }
                        },
                        "Subject": {
                            "Charset": CHARSET,
                            "Data": record['Sns']['Subject'],
                        },
                    },
                    Source=os.environ['dev.kolayemi@gmail.com'],
                )
                print(response)

    except Exception as e:
        # Send some context about this error to Lambda Logs
        print(e)
        raise e
    