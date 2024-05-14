import json
from models.slack.service import SlackService
from models.chat.service import ChatService


def lambda_handler(event, context):
    event_body = event["Records"][0]["body"]
    slack_event = json.loads(event_body).get("event")
    print(slack_event)
    """
    SlackService 인스턴스 생성 및 슬랙 대화 내용 추출
    """
    slack = SlackService(slack_event)
    # 인터랙티브 메시지 전송
    slack.post_thread_message("Thinking...")

    history = slack.get_slack_history()  # 대화 내용 추출
    print(history)
    # 사용자 입력 추출
    bot_id = slack_event["blocks"][0]["elements"][0]["elements"][0]["user_id"]
    user_input = slack_event["text"].replace(f"<@{bot_id}> ", "")

    # print(bot_id)
    # print(user_input)
    """
    ChatGPT 대화 생성
    """
    chat = ChatService()
    # 대화 내용 생성
    text = chat.chat_with_chatgpt(user_input, history)

    # """
    # 슬랙으로 메시지 전송
    # """
    # slack.post_thread_message(text)
    """
    Thinking 메시지 업데이트
    """
    slack.edit_thread_message(text)

    return {"statusCode": 200, "body": ""}
