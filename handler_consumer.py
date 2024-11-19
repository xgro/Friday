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

    # 대화 내용 추출
    history = slack.get_slack_history()

    # 사용자 입력 추출
    user_input = slack.get_user_input()

    """
    ChatGPT 대화 생성
    """
    chat = ChatService()

    """
    슬랙으로 메시지 전송
    """
    full_sentence = ""
    for response_chunk in chat.generate_response(user_input, history):
        slack.edit_thread_message(response_chunk)
        full_sentence += response_chunk

    return {"statusCode": 200, "body": ""}
