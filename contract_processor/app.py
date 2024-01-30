import json
import boto3
import sys
import os

SUCCESS=0


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
    print(json.dumps(event))
    try:
        sns_client = boto3.client('sns')

        # Add status to event
        event['Status']=SUCCESS
        event['Type']="ContractStatus"
        print(json.dumps(event))

        # Publish message to topic
        response = sns_client.publish(
            TopicArn=os.environ['TOPIC_ARN'],
            Subject="EDP Workflow Status",
            Message=json.dumps(event)
        )
        print(response)

    except Exception as e:
        # Send some context about this error to Lambda Logs
        print(e)
        raise e

    # test
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "message sent via " + os.environ['TOPIC_ARN'],
        }),
    }
