import os
from slack_sdk import WebClient


class SlackService:
    def __init__(self, slack_event):
        # 슬랙 토큰 설정
        token = os.environ.get("SLACK_TOKEN")
        self.client = WebClient(
            token,
        )

        # 슬랙 클라이언트 인스턴스 생성
        self.channel = slack_event.get("channel")
        self.ts = slack_event.get("ts")
        self.thread_ts = slack_event.get("thread_ts")
        self.bot_id = self.client.auth_test().data["user_id"]  # type: ignore
        self.user_input = slack_event.get("text").replace(f"<@{self.bot_id}> ", "")

    def get_user_input(self):
        # 사용자 입력 추출
        return self.user_input

    def get_message(self):
        # conversations_replies() 메서드 호출
        ts = self.thread_ts
        if self.thread_ts is None:
            ts = self.ts

        result = self.client.conversations_replies(
            channel=self.channel,
            ts=ts,
        )
        # 메시지 추출
        return result.data["messages"]  # type: ignore

    def post_thread_message(self, text):
        # chat_postMessage() 메서드 호출
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            }
        ]

        return self.client.chat_postMessage(
            channel=self.channel,
            text="Post Message",
            blocks=blocks,
            thread_ts=self.ts,
        )

    def edit_thread_message(self, text):
        # chat_update() 메서드 호출
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text.replace(f"<@{self.bot_id}> ", ""),
                },
            }
        ]

        messages = self.get_message()
        bot_messages = []
        for i in messages:
            # print(i)
            # print("ts", i["ts"])
            if "bot_id" not in i:
                continue
            # if "Edit" not in i["text"]:
            #     continue
            # if "Thinking" in i["blocks"][0]["text"]["text"]:
            bot_messages.append(i)

        # print(messages)

        if len(messages) == 0:
            return

        # print(blocks)

        lastest_bot_message = bot_messages[-1]
        ts = lastest_bot_message["ts"]

        print(f"lastest_bot_message: {lastest_bot_message}")
        print(f"ts: {ts}")

        self.client.chat_update(
            channel=self.channel,
            ts=ts,
            text="Edit Message",
            blocks=blocks,
        )

    def get_slack_history(self):
        """
        이전 슬랙내용이 존재하는 경우, 이전 대화 내용을 conversation에 추가
        """
        if self.thread_ts is None:
            return []

        history = []
        messages = self.get_message()
        for i in messages:
            # 봇의 메시지 중 "thinking"이 포함된 메시지는 제외
            if "bot_id" in i:
                if "Thinking" in i["blocks"][0]["text"]["text"]:
                    continue

            # 사용자의 입력 중 봇 멘션이 있는 경우 사용자의 입력으로 처리
            if f"<@{self.bot_id}>" in i["text"]:
                history.append(
                    {
                        "role": "user",
                        "content": i["text"].replace(f"<@{self.bot_id}> ", ""),
                    }
                )

            # 메시지에 bot_id가 있는 경우 봇의 응답으로 처리
            if "bot_id" in i:
                history.append(
                    {
                        "role": "assistant",
                        "content": i["blocks"][0]["text"]["text"],
                    }
                )

        conversation = []
        topics = 11
        start_index = max(0, len(history) - topics)
        end_index = len(history) - 1
        for i in range(start_index, end_index):
            # logger.info(pre_prompt[i])
            conversation.append(history[i])
        return conversation
