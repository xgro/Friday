import os
import openai

from models.slack.service import SlackService


class ChatService:
    def __init__(self) -> None:
        self.model = os.environ.get("MODEL") or "gpt-3.5-turbo"
        self.system_prompt = os.environ.get("SYSTEM_PROMPT")
        self.client = openai
        self.stream = os.environ.get("STREAM") or False

    def generate_response(
        self,
        user_input: str,
        history: list,
    ):
        """대화 내용 작성"""
        conversation = []
        # 시스템 이름 및 시스템 프롬프트 추가
        contents = f"""
- System name is Friday. 
- {self.system_prompt}
- You must reply politely.
- this is a conversation between a user and a system as Slack messages.
- When you explain the code blocks, you must no contain the language in the code block."""

        conversation.append(
            {
                "role": "system",
                "content": contents,
            }
        )

        # 이전 대화 내용 추가
        conversation += history

        # 사용자 입력 추가
        conversation.append({"role": "user", "content": user_input})

        text = ""
        buffer = ""
        buffer_text = ""

        first_chunk_received = False

        """
        Thinking 메시지 업데이트
        """
        # print("response: ", response)
        stream = self.stream
        if stream == "true":
            stream = True
        else:
            stream = False

        if stream:
            for chunk in self.client.ChatCompletion.create(
                model=self.model,
                messages=conversation,
                stream=stream,
            ):
                if "content" in chunk["choices"][0]["delta"]:
                    text_chunk = chunk["choices"][0]["delta"]["content"]
                    buffer += text_chunk
                    text += text_chunk

                    if not first_chunk_received:
                        first_chunk_received = True
                        continue  # 첫번째 빈 문자를 보내는 것을 방지

                    if len(buffer) >= 150:
                        buffer_text += buffer
                        buffer = ""
                        # 메시지 업데이트
                        yield buffer_text
                        # print(f"Updated message: {text}")

            if buffer:
                buffer_text += buffer
                yield buffer_text
        else:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=conversation,
            )

            text = response["choices"][0]["message"]["content"]
            yield text
