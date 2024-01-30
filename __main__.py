"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

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

# Lambda function
lambda_function = aws.lambda_.Function('notification-manager',
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./notification_manager")}),
    role=lambda_role.arn,
    handler='notification_manager.lambda_handler',
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
sns_subscription = aws.sns.TopicSubscription(f'{project_name}-Subscription',
    topic=sns_topic.arn,
    protocol='lambda',
    endpoint=lambda_function.arn
)

# SSM Parameter to store the SNS topic URL
sns_topic_url_param = aws.ssm.Parameter('EventTopicArn',
    name='EventTopicArn',  # Name of the parameter
    type='String',       # Type of the parameter (String, StringList, SecureString)
    value=sns_topic.arn  # The actual value to store, here ARN is used as the URL identifier for the SNS Topic
)

# SSM Parameter to store the Lambda function name
lambda_function_name_param = aws.ssm.Parameter('notificationManagerlambdaFunctionName',
    name='notificationManager',    # Name of the parameter
    type='String',               # Type of the parameter (String, StringList, SecureString)
    value=lambda_function.name   # The actual value to store, which is the name of the Lambda Function
)

# Export the ARNs of the SNS topic, the Lambda function and the parameter names 
pulumi.export('sns_topic_arn', sns_topic.arn)
pulumi.export('lambda_function_arn', lambda_function.arn)
pulumi.export('sns_topic_url_param_name', sns_topic_url_param.name)
pulumi.export('lambda_function_name_param_name', lambda_function_name_param.name)
