"""Contract Processor Lambda Function"""
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
        sns_client = boto3.client('sns')

        # Add status to event
        event['status']=SUCCESS
        event['type']="ContractStatus"
        print(json.dumps(event))

        # Publish message to topic
        response = sns_client.publish(
            TopicArn=os.environ['TOPIC_ARN'],
            Subject="Workflow Status",
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
