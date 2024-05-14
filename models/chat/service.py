import os
import openai


class ChatService:
    def __init__(self) -> None:
        self.model = os.environ.get("MODEL") or "gpt-3.5-turbo"
        self.system_prompt = os.environ.get("SYSTEM_PROMPT")
        self.client = openai

    def chat_with_chatgpt(self, user_input, history: list):
        """
        대화 내용 작성
        """
        conversation = []
        # 시스템 이름 및 시스템 프롬프트 추가
        contents = f"""
- System name is Friday. 
- {self.system_prompt}
- this is a conversation between a user and a system as Slack messages.
- you must follow the Slack message format.
- When you explain the code blocks, you must no contain the language in the code block.

eg. Bold text must be "*bold*",do not use "**bold**" in the plain text.
if you want to use code block, use Bold text "**bold**" in the code block.

Basic formatting with mrkdwn:
Bold: *bold*
Italic: _italic_
Strikethrough: ~strike~
Blockquote: >quote
Code: `code block`
Code blocks: ```code blocks```
Link: <https://www.example.com>
New line: \n"""
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

        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=conversation,
        )
        return response.choices[0].message.content  # type: ignore
