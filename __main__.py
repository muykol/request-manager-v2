"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import json 

project_name = 'request_manager_pulumi_dojo'

# Define an AWS Lambda function
lambda_role = aws.iam.Role(f'{project_name}-lambdaRole', 
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }]
    }"""
)

# Attach the AWSLambdaBasicExecutionRole policy to the role
role_policy_attachment = aws.iam.RolePolicyAttachment('lambdaRoleAttachment',
    role=lambda_role.name,
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
)

# Lambda functions
lambda_function = aws.lambda_.Function('notification-manager',
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./notification_manager")}),
    role=lambda_role.arn,
    handler='notification_manager.lambda_handler',
    runtime='python3.10'
)

lambda_function = aws.lambda_.Function('contract_processor',
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./contract_processor")}),
    role=lambda_role.arn,
    handler='contract_processor.lambda_handler',
    runtime='python3.10'
)

# Define an SNS topic
sns_topic = aws.sns.Topic('EventTopic')

# Give the Lambda permission to be invoked by the SNS topic
lambda_permission = aws.lambda_.Permission(f'{project_name}-LambdaPermission',
    action='lambda:InvokeFunction',
    function=lambda_function.name,
    principal='sns.amazonaws.com',  
    source_arn=sns_topic.arn
)

# Subscribe the Lambda function to the SNS topic
snsLambda_subscription = aws.sns.TopicSubscription('snsLambda-Subscription',
    topic=sns_topic.arn,
    protocol='lambda',
    endpoint=lambda_function.arn
)

# Create an SQS queue
sqs_queue = aws.sqs.Queue('request_manager_queue')
request_policy_document = sqs_queue.arn.apply(lambda arn: aws.iam.get_policy_document_output(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    sid="First",
    effect="Allow",
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="*",
        identifiers=["*"],
    )],
    actions=["sqs:SendMessage"],
    resources=[arn],
    conditions=[aws.iam.GetPolicyDocumentStatementConditionArgs(
        test="ArnEquals",
        variable="aws:SourceArn",
        values=[sns_topic["EventTopic"]["arn"]],
    )],
)]))
request_queue_policy = aws.sqs.QueuePolicy("requestQueuePolicy",
    queue_url=sqs_queue.id,
    policy=request_policy_document.json)

snsSqs_subscription = aws.sns.TopicSubscription('snsSqs-Subscription',
    topic=sns_topic.arn,
    protocol='sqs',
    endpoint=sqs_queue.arn
)


# # Create an SQS queue policy to allow the SNS topic to publish to the SQS queue
# queue_policy = sqs_queue.arn.apply(lambda arn: json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [{
#             "Effect": "Allow",
#             "Principal": {"Service": "sns.amazonaws.com"},
#             "Action": "sqs:SendMessage",
#             "Resource": arn,
#             "Condition": {
#                 "ArnEquals": {"aws:SourceArn": sns_topic.arn}
#             }
#         }]
#     }))
# queue_policy_resource = aws.sqs.QueuePolicy(
#     'request-manager-queue-policy',
#     queue_url=sqs_queue.id,
#     policy=queue_policy # Here queue_policy is already a JSON string, not an Output object
# )

# SSM Parameter to store the SNS topic URL
sns_topic_url_param = aws.ssm.Parameter('EventTopicArn',
    name='EventTopicArn',  # Name of the parameter
    type='String',       # Type of the parameter (String, StringList, SecureString)
    value=sns_topic.arn  # The actual value to store, here ARN is used as the URL identifier for the SNS Topic
)

# SSM Parameter to store the Lambda function name
lambda_function_name_param = aws.ssm.Parameter('contractProcessorName',
    name='contractProcessor',    # Name of the parameter
    type='String',               # Type of the parameter (String, StringList, SecureString)
    value=lambda_function.name   # The actual value to store, which is the name of the Lambda Function
)

# Store the SQS queue URL in the AWS SSM Parameter Store
ssm_parameter = aws.ssm.Parameter('request_manager_queue_url',
    name='request_manager_queue',
    type='String',
    value=sqs_queue.id
)

# Export the ARNs of the SNS topic, the Lambda function and the parameter names 
pulumi.export('sns_topic_arn', sns_topic.arn)
pulumi.export('lambda_function_arn', lambda_function.arn)
pulumi.export('sns_topic_url_param_name', sns_topic_url_param.name)
pulumi.export('lambda_function_name_param_name', lambda_function_name_param.name)
pulumi.export('queue_url', sqs_queue.id)
pulumi.export('queue_policy', queue_policy)
pulumi.export('ssm_parameter_name', ssm_parameter.name)
