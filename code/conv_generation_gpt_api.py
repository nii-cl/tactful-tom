import openai
openai.api_key = "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"

def generate_natural_conversation_step1(filled_step_text: str) -> str:
    """
    调用 OpenAI ChatCompletion API，
    传入 filled_step_text 作为 user 消息，
    返回模型的文本回复。
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in dialogue generation and natural conversation. Engage in fluent, context-aware, and coherent dialogues while maintaining consistency\
                                 The conversation should consist of 10 exchanges."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": filled_step_text
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

def generate_natural_conversation_step2(filled_step_text: str) -> str:
    """
    调用 OpenAI ChatCompletion API，
    传入 filled_step_text 作为 user 消息，
    返回模型的文本回复。
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in dialogue generation and natural conversation. Engage in fluent, context-aware, and coherent dialogues while maintaining consistency\
                                 The conversation should consist of 6 exchanges."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": filled_step_text
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

def generate_natural_conversation_step3(filled_step_text: str) -> str:
    """
    调用 OpenAI ChatCompletion API，
    传入 filled_step_text 作为 user 消息，
    返回模型的文本回复。
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in dialogue generation and natural conversation. Engage in fluent, context-aware, and coherent dialogues while maintaining consisteny.\
                                 The conversation should consist of 6 exchanges."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": filled_step_text
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

def generate_natural_conversation_step4(filled_step_text: str) -> str:
    """
    调用 OpenAI ChatCompletion API，
    传入 filled_step_text 作为 user 消息，
    返回模型的文本回复。
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in dialogue generation and natural conversation. Engage in fluent, context-aware, and coherent dialogues while maintaining consisteny.\
                                 The conversation should consist of 6 exchanges."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": filled_step_text
                    }
                ]
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

# # 使用示例
# if __name__ == "__main__":
#     some_text = "This is a sample conversation prompt."
#     result = generate_natural_conversation(some_text)
#     print(result)ååå