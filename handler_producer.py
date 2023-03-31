import json
import boto3
import os

QUEUE_URL = os.getenv('QUEUE_URL')
API_APP_ID = os.getenv('API_APP_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def lambda_handler(event, context):
    try:
        slack_body  = event['body']
        slack_event = json.loads(slack_body)
        
        if "challenge" in slack_event:
            challenge_answer = slack_event.get("challenge")
            print(challenge_answer)
            return { 'statusCode': 200, 'body': challenge_answer }
        
        SQS = boto3.client('sqs')
        SQS.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=slack_body
        )

        # TODO implement
        return {
            'statusCode': 200,
            'body': ""
        }
        
    except:
        return {
            'statusCode': 400,
            'body': ""
        }

