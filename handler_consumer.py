import json
import os
import logging
import openai
from slack_sdk import WebClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BOT_NAME = os.environ.get("BOT_NAME")
MODEL_ID = os.environ.get("MODEL_ID")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
# Key 설정
openai.api_key = os.environ.get("OPENAI_KEY")

class SlackAPI:
    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)

    def get_message_ts(self, channel_id, thread_ts):
        # conversations_replies() 메서드 호출
        result = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
        
        # 메시지 추출
        messages = result.data['messages']
        # print(messages, len(messages))
        if len(messages) > 0:
            res = []
            for i in messages:
                if "bot_id" not in i:
                    continue
                text = i["text"]
                res.append(text)
        return res

    def post_thread_message(self, channel_id, message_ts, text):
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel = channel_id,
            text = text,
            thread_ts = message_ts
        )
        return result

def ChatGPT_conversation(conversation=[]):
    response = openai.ChatCompletion.create(
        # max_tokens = 500,
        model = MODEL_ID,
        messages = conversation
    )
    total_tokens = response['usage']['total_tokens']
    logger.info(f"Total tokens used: {total_tokens}")
        
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation
        

def lambda_handler(event, context):
    # print(f"Received event:\n{event}\nWith context:\n{context}")
    slack = SlackAPI(SLACK_TOKEN)
    slack_body = event['Records'][0]['body']

    slack_event = json.loads(slack_body)
    channel_id =  slack_event.get("event").get("channel")
    message_ts = slack_event.get("event").get("ts")
    
    """
    대화 내용 작성
    """
    conversation = []
    # conversation.append({'role': 'system', 'content': f"Name is ${BOT_NAME}, Response must not exceed 300 characters."})
    conversation.append({'role': 'system', 'content': f"System name is {BOT_NAME}, Please reply in Korean Respond."})

    if "thread_ts" in slack_event.get("event"):
        thread_ts = slack_event.get("event").get("thread_ts")
        pre_prompt = slack.get_message_ts(channel_id,thread_ts)

        # if len(pre_prompt) > 0:
        #     conversation.append({'role': 'assistant', 'content': pre_prompt[-1]})

        for i in range(max(0,len(pre_prompt)-3),len(pre_prompt)):
            logger.info(pre_prompt[i])
            conversation.append({'role': 'system', "name": BOT_NAME, 'content': pre_prompt[i]})

    prompt = slack_event.get("event").get("text")
    conversation.append({'role': 'user', 'content': prompt})

    """
    ChatGPT 대화 생성
    """
    conversation = ChatGPT_conversation(conversation)
    
    # 마지막 대화 내용 추출
    response_text = conversation[-1]['content'].strip()
    
    """
    슬랙으로 메시지 전송
    """
    slack.post_thread_message(channel_id, message_ts, response_text)

    return {
        'statusCode': 200,
        'body': ""
    }