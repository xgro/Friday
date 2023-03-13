import json
import os
import logging
from slack_sdk import WebClient
import openai

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BOT_NAME = os.environ.get("BOT_NAME")
MODEL_ID = os.environ.get("MODEL_ID")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_KEY")

class SlackAPI:
    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)

    def get_message_ts(self, channel_id, thread_ts):
        # conversations_replies() 메서드 호출
        result = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
        # logger.info(result, channel_id, thread_ts)
        # 메시지 추출
        messages = result.data['messages']
        
        # 메시지가 존재할 경우, 메시지 추출
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
    # Key 설정
    openai.api_key = OPENAI_KEY
    
    # 프롬프트 전송
    response = openai.ChatCompletion.create(
        model = MODEL_ID,
        messages = conversation
    )
    # 사용한 토큰값 확인하고 싶을 때 사용
    # print(f'{response["usage"]["prompt_tokens"]} prompt tokens used.')
    
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation

def lambda_handler(event, context):
    # TOKEN 설정
    slack = SlackAPI(SLACK_TOKEN)
    
    # Producer에서 전달받은 이벤트 추출
    slack_body = event['Records'][0]['body']
    slack_event = json.loads(slack_body)
    
    # channel_id 및 message_ts 추출
    channel_id =  slack_event.get("event").get("channel")
    message_ts = slack_event.get("event").get("ts")
    
    # OpenAI GPT-3 챗봇과 대화를 위한 프롬프트 생성
    conversation = []
    
    # Conversation에 System name 추가 
    conversation.append({'role': 'system', 'content': f"System name is {BOT_NAME}, Plz reply in Korean"})

    if "thread_ts" in slack_event.get("event"):
        thread_ts = slack_event.get("event").get("thread_ts")
        pre_prompt = slack.get_message_ts(channel_id,thread_ts)
        
        # 토큰값을 절약하기 위해서, 최근 N개의 메시지만 사용
        for i in range(max(0,len(pre_prompt)-3),len(pre_prompt)):
            # logger.info(pre_prompt[i])
            conversation.append({'role': 'system', "name": BOT_NAME, 'content': pre_prompt[i]})
    
    # Conversation에 User가 보낸 메시지 추가
    prompt = slack_event.get("event").get("text")
    conversation.append({'role': 'user', 'content': prompt})
    
    # OpenAI GPT-3 챗봇과 대화
    conversation = ChatGPT_conversation(conversation)
    
    # OpenAI GPT-3 챗봇의 대답을 Slack에 전송
    response_text = conversation[-1]['content'].strip()
    slack.post_thread_message(channel_id, message_ts, response_text)
    
    return {
        'statusCode': 200,
        'body': ""
    }