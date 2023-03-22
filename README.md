# **ChatGPT using Slack Bot**

Here is an introduction to implementing ChatGPT, a chatbot using Slack bot and OpenAI's GPT-3.5. We will implement a Slack Bot using AWS Lambda and call the `**gpt-3.5-turbo**` API to perform question answering.

# Features

- `gpt-3.5-turbo` 기반의 api를 사용하여 나만의 챗봇을 구축할 수 있습니다.
- 스레드에서 최대 5개의 대화 히스토리를 추적하여 답변을 생성합니다.
- serverless architecture 구성으로 인해 인프라 비용이 거의 들지 않습니다.

![2023-03-22 15;42;08](https://user-images.githubusercontent.com/76501289/226831302-705202d4-4ae4-4e88-9587-06f98bd82c28.gif)

# Prequisite

1. Create an [OpenAI account](https://openai.com/api/) and [get an API Key](https://platform.openai.com/account/api-keys)
2. Create an [AWS account](https://aws.amazon.com/es/)
3. Setup your Slack bot. You can follow [this instructions](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to get your token.

# Architecture
![image](https://user-images.githubusercontent.com/76501289/226831214-1956651a-9024-449e-9557-eab46bb94953.png)

# More Informations
[xgro's velog](https://velog.io/@xgro/awsslackbotchatgpt)
