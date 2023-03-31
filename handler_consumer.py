import json
import os
import logging
import openai
from slack_sdk import WebClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ENV 설정
BOT_NAME = os.environ.get("BOT_NAME")
MODEL_ID = os.environ.get("MODEL_ID")
HISTORY = os.environ.get("HISTORY")
SYSTEM_PROMPT=os.environ.get("SYSTEM_PROMPT")

# Key 설정
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
openai.api_key = os.environ.get("OPENAI_TOKEN")

class SlackAPI:
    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)

    def get_message_ts(self, channel_id, thread_ts):
        # conversations_replies() 메서드 호출
        bot_id = self.client.auth_test().data['user_id']
        result = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
        # 메시지 추출
        messages = result.data['messages']
        # print(messages, len(messages))
        if len(messages) > 0:
            res = []
            for i in messages:
                if f"<@{bot_id}>" in i["text"]:
                    name = "example_user"
                    text = i["text"].replace(f"<@{bot_id}>","")
                    res.append({'role': 'system', 'name': name, 'content': text})
                if "bot_id" in i:
                    name = "example_assistant"
                    text = i["text"]
                    res.append({'role': 'system', 'name': name, 'content': text})
            return res
        return []

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
    slack = SlackAPI(SLACK_TOKEN)
    slack_body = event['Records'][0]['body']

    slack_event = json.loads(slack_body)
    channel_id =  slack_event.get("event").get("channel")
    message_ts = slack_event.get("event").get("ts")
    
    """
    대화 내용 작성
    """
    conversation = []
    conversation.append({'role': 'system', 'content': f"System name is {BOT_NAME}. {SYSTEM_PROMPT}"})

    """
    이전 슬랙내용이 존재하는 경우, 이전 대화 내용을 conversation에 추가
    """
    if "thread_ts" in slack_event.get("event"):
        thread_ts = slack_event.get("event").get("thread_ts")
        pre_prompt = slack.get_message_ts(channel_id,thread_ts)

        if len(pre_prompt) > 0:
            topics = int(HISTORY)*2+1
            for i in range(max(0,len(pre_prompt)-topics),len(pre_prompt)-1):
                logger.info(pre_prompt[i])
                conversation.append(pre_prompt[i])
                
    prompt = slack_event.get("event").get("text")
    conversation.append({'role': 'user', 'content': prompt})
    
    """
    ChatGPT 대화 생성
    """
    conversation = ChatGPT_conversation(conversation)
    
    # 마지막 대화 내용 추출
    res= conversation[-1]['content'].strip()
    
    """
    슬랙으로 메시지 전송
    """
    slack.post_thread_message(channel_id, message_ts, res)

    return {
        'statusCode': 200,
        'body': ""
    }