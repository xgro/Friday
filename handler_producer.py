import json
import boto3
import os

QUEUE_URL = os.getenv('QUEUE_URL')
API_APP_ID = os.getenv('API_APP_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def lambda_handler(event, context):
    slack_body  = event['body']
    slack_event = json.loads(slack_body)
    
    if "challenge" in slack_event:
        challenge_answer = slack_event.get("challenge")
        print(challenge_answer)
        return { 'statusCode': 200, 'body': challenge_answer }
    
    # if not slack_event.get("api_app_id"):
    #     raise ValueError 
    
    # if API_APP_ID != slack_event.get("api_app_id"):
    #     raise ValueError
    
    # if slack_event.get("event").get("channel") != CHANNEL_ID:
    #     raise ValueError
    
    SQS = boto3.client('sqs')
    # print(team_id)
    SQS.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=slack_body
    )

    # TODO implement
    return {
        'statusCode': 200,
        'body': ""
    }

